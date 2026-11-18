import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parent
SIZE = (1400, 1000)
STUDIO = (0.92, 0.90, 0.86)
BLACK = (0.012, 0.012, 0.012)
STUDIO_EYE = (620.0, -690.0, 345.0)
PROFILE_EYE = (0.0, -850.0, 120.0)
FOCUS = (0.0, 0.0, 110.0)


def location_matrix(loc):
    trsf = loc.wrapped.Transformation()
    matrix = np.eye(4, dtype=np.float64)
    for i in range(3):
        for j in range(4):
            matrix[i, j] = trsf.Value(i + 1, j + 1)
    if not np.isfinite(matrix).all():
        raise ValueError("Non-finite CadQuery placement matrix")
    return matrix


def vtk_transform(matrix):
    import vtk

    placement = vtk.vtkMatrix4x4()
    placement.Identity()
    for i in range(3):
        for j in range(4):
            placement.SetElement(i, j, float(matrix[i, j]))
    transform = vtk.vtkTransform()
    transform.SetMatrix(placement)
    return transform


def mesh_part(solid, anchor_location, part_key):
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    vertices, faces = solid.moved(anchor_location).tessellate(0.7, 0.18)
    if not vertices or not faces:
        raise ValueError(f"Empty tessellation for catalogue part {part_key!r}")

    points = vtk.vtkPoints()
    points.SetDataTypeToDouble()
    points.SetNumberOfPoints(len(vertices))
    for i, vertex in enumerate(vertices):
        points.SetPoint(i, vertex.x, vertex.y, vertex.z)

    cells = vtk.vtkCellArray()
    triangle = vtk.vtkTriangle()
    ids = triangle.GetPointIds()
    for a, b, c in faces:
        ids.SetId(0, a)
        ids.SetId(1, b)
        ids.SetId(2, c)
        cells.InsertNextCell(triangle)

    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)

    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(poly)
    clean.SetTolerance(0.0)
    clean.ConvertPolysToLinesOff()
    clean.ConvertLinesToPointsOff()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(clean.GetOutputPort())
    normals.ComputePointNormalsOn()
    normals.ComputeCellNormalsOff()
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOff()
    normals.SplittingOn()
    normals.SetFeatureAngle(45.0)
    normals.Update()

    mesh = normals.GetOutput()
    if mesh.GetNumberOfPolys() == 0 or mesh.GetPointData().GetNormals() is None:
        raise RuntimeError(f"VTK could not compute shaded triangles for {part_key!r}")

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    mapper.ScalarVisibilityOff()
    return mapper, vtk_to_numpy(mesh.GetPoints().GetData())


def surface_property(part_key, pigment, category, material, palette):
    import vtk

    value = palette[pigment]
    rgba = np.asarray(value.toTuple() if hasattr(value, "toTuple") else value, dtype=float)
    if rgba.shape != (4,) or not np.isfinite(rgba).all() or np.any((rgba < 0) | (rgba > 1)):
        raise ValueError(f"Invalid palette RGBA for pigment {pigment!r}: {value!r}")

    fields = [str(v).strip().casefold() for v in (part_key, pigment, category, material)]
    description = " ".join(fields)
    words = set(re.findall(r"[a-z]+", description))
    luminous = (
        "opal" in description
        or bool(words & {"led", "leds", "emitter", "emissive", "luminous", "diffuser"})
        or any(field in {"light", "warm_light", "warm light"} for field in fields)
    )
    rgb = rgba[:3]
    if luminous:
        rgb = 0.65 * rgb + 0.35 * np.array((1.0, 0.92, 0.76))

    prop = vtk.vtkProperty()
    prop.SetInterpolationToPhong()
    prop.SetColor(*rgb)
    prop.SetOpacity(float(rgba[3]))
    prop.SetDiffuse(0.8)
    prop.SetAmbient(0.55 if luminous else 0.15)
    prop.SetSpecular(0.15)
    prop.SetSpecularColor(1.0, 1.0, 1.0)
    prop.SetSpecularPower(35.0)
    return prop


def install_pose(renderer, items, catalogue, palette, cache):
    import vtk

    renderer.RemoveAllViewProps()
    instances = []
    for instance_name, (part_key, loc, _) in items.items():
        if part_key not in catalogue:
            raise KeyError(f"Unknown part {part_key!r} in instance {instance_name!r}")
        placement = location_matrix(loc)
        if part_key not in cache:
            solid, pigment, category, material = catalogue[part_key]
            mapper, vertices = mesh_part(solid, loc, part_key)
            prop = surface_property(part_key, pigment, category, material, palette)
            cache[part_key] = mapper, vertices, prop, np.linalg.inv(placement)

        mapper, vertices, prop, inverse_anchor = cache[part_key]
        anchor_to_instance = placement @ inverse_anchor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetProperty(prop)
        actor.SetUserTransform(vtk_transform(anchor_to_instance))
        renderer.AddActor(actor)
        instances.append((vertices, anchor_to_instance))

    if not instances:
        raise ValueError("build.layout returned no instances")
    return instances


def frame_camera(renderer, instances, eye_position):
    eye = np.asarray(eye_position, dtype=float)
    focus = np.asarray(FOCUS, dtype=float)
    forward = focus - eye
    forward /= np.linalg.norm(forward)
    vertical = np.array((0.0, 0.0, 1.0))
    right = np.cross(forward, vertical)
    right /= np.linalg.norm(right)
    axes = np.column_stack((right, np.cross(right, forward)))

    lower = np.full(2, np.inf)
    upper = np.full(2, -np.inf)
    for vertices, placement in instances:
        projection = vertices @ (placement[:3, :3].T @ axes)
        offset = (placement[:3, 3] - focus) @ axes
        lower = np.minimum(lower, projection.min(axis=0) + offset)
        upper = np.maximum(upper, projection.max(axis=0) + offset)

    width, height = upper - lower
    half_span = 0.5 * max(width * SIZE[1] / SIZE[0], height)
    if not math.isfinite(half_span) or half_span <= 0.0:
        raise ValueError("The located CAD mesh has invalid projected bounds")

    shift = axes @ ((lower + upper) * 0.5)
    scale = float(np.clip(175.0, half_span / 0.78, half_span / 0.68))
    camera = renderer.GetActiveCamera()
    camera.SetPosition(*(eye + shift))
    camera.SetFocalPoint(*(focus + shift))
    camera.SetViewUp(*vertical)
    camera.OrthogonalizeViewUp()
    camera.ParallelProjectionOn()
    camera.SetParallelScale(scale)
    renderer.ResetCameraClippingRange()


def make_scene():
    import vtk

    renderer = vtk.vtkRenderer()
    renderer.AutomaticLightCreationOff()
    renderer.GradientBackgroundOff()
    renderer.SetAmbient(1.0, 1.0, 1.0)
    renderer.SetUseDepthPeeling(True)
    renderer.SetMaximumNumberOfPeels(48)
    renderer.SetOcclusionRatio(0.0)
    renderer.SetUseFXAA(True)

    lights = (
        ((-270.0, -390.0, 650.0), (1.00, 0.96, 0.91), 0.84),
        ((480.0, -220.0, 265.0), (0.88, 0.94, 1.00), 0.38),
        ((210.0, 350.0, 465.0), (1.00, 0.97, 0.91), 0.50),
    )
    for position, color, intensity in lights:
        light = vtk.vtkLight()
        light.SetLightTypeToSceneLight()
        light.SetPosition(*position)
        light.SetFocalPoint(*FOCUS)
        light.SetPositional(True)
        light.SetConeAngle(85.0)
        light.SetExponent(1.0)
        light.SetAttenuationValues(1.0, 0.0, 0.0)
        light.SetColor(*color)
        light.SetAmbientColor(0.0, 0.0, 0.0)
        light.SetIntensity(intensity)
        renderer.AddLight(light)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetAlphaBitPlanes(1)
    window.SetMultiSamples(0)
    window.SetSize(*SIZE)
    window.AddRenderer(renderer)
    return renderer, window


def inspect_png(path, background):
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"VTK did not write {path.name}")

    with Image.open(path) as source:
        if source.format != "PNG" or source.size != SIZE:
            raise RuntimeError(f"Invalid output for {path.name}: {source.format}, {source.size}")
        image = source.convert("RGB")

    rgb = np.asarray(image)
    expected = np.rint(np.array(background) * 255).astype(np.int16)
    corners = rgb[[0, 0, -1, -1], [0, -1, 0, -1]].astype(np.int16)
    if np.max(np.abs(corners - expected)) > 3:
        raise RuntimeError(
            f"{path.name}: unexpected framebuffer background {corners.tolist()}, "
            f"expected {expected.tolist()}. Check the VTK offscreen OpenGL context."
        )

    difference = np.max(np.abs(rgb.astype(np.int16) - corners[0]), axis=2)
    count = int(np.count_nonzero(difference > 6))
    coverage = count / (SIZE[0] * SIZE[1])
    variation = math.sqrt(sum(s * s for s in ImageStat.Stat(image).stddev) / 3.0) / 255.0
    if coverage <= 0.02 or variation <= 0.03:
        raise RuntimeError(
            f"{path.name} failed CAD render validation: foreground fraction={coverage:.6f}, "
            f"RGB variation={variation:.6f}. Check the VTK offscreen OpenGL context "
            "and the model's material visibility."
        )
    return {
        "file": f"render/{path.name}",
        "resolution": list(SIZE),
        "foreground_pixels": count,
        "foreground_fraction": round(coverage, 8),
        "rgb_variation_fraction": round(variation, 8),
    }


def render_all():
    import vtk

    os.chdir(ROOT)
    if not (ROOT / "build.py").is_file():
        raise FileNotFoundError(f"Missing {ROOT / 'build.py'}")
    sys.path.insert(0, str(ROOT))
    import build

    if Path(build.__file__).resolve() != (ROOT / "build.py").resolve():
        raise ImportError("The imported build module is not the adjacent build.py")

    catalogue = build.catalogue()
    palette = build.PALETTE() if callable(build.PALETTE) else build.PALETTE
    output = ROOT / "render"
    output.mkdir(exist_ok=True)
    if not output.resolve().is_relative_to(ROOT):
        raise RuntimeError("The render output directory resolves outside the script folder")

    renderer, window = make_scene()
    errors = []

    @vtk.calldata_type(vtk.VTK_STRING)
    def on_error(caller, event, message=None):
        errors.append(f"{caller.GetClassName()}: {message or event}")

    window.AddObserver("ErrorEvent", on_error)
    renderer.AddObserver("ErrorEvent", on_error)
    cache = {}
    records = []

    with tempfile.TemporaryDirectory(prefix=".cad-render-", dir=output) as tmp:
        stage = Path(tmp)

        def capture(name, background):
            renderer.SetBackground(*background)
            window.Render()
            if errors:
                raise RuntimeError(f"VTK offscreen render failed for {name}: {'; '.join(errors)}")

            capture_filter = vtk.vtkWindowToImageFilter()
            capture_filter.AddObserver("ErrorEvent", on_error)
            capture_filter.SetInput(window)
            capture_filter.SetInputBufferTypeToRGB()
            capture_filter.ReadFrontBufferOff()
            capture_filter.ShouldRerenderOff()
            capture_filter.Update()

            path = stage / name
            writer = vtk.vtkPNGWriter()
            writer.AddObserver("ErrorEvent", on_error)
            writer.SetFileName(str(path))
            writer.SetInputConnection(capture_filter.GetOutputPort())
            writer.Write()
            if errors or writer.GetErrorCode() != 0:
                raise RuntimeError(
                    f"VTK framebuffer capture or PNG write failed for {name}: "
                    f"writer code {writer.GetErrorCode()}; {'; '.join(errors)}"
                )
            records.append(inspect_png(path, background))

        try:
            for pose, t in (("closed", 0.0), ("middle", 0.5), ("open", 1.0)):
                items, _ = build.layout(t)
                instances = install_pose(renderer, items, catalogue, palette, cache)
                frame_camera(renderer, instances, STUDIO_EYE)
                capture(f"{pose}_studio.png", STUDIO)
                capture(f"{pose}_black.png", BLACK)
                if pose == "open":
                    frame_camera(renderer, instances, PROFILE_EYE)
                    capture("open_side.png", STUDIO)
        finally:
            window.Finalize()

        summary = {
            "ok": True,
            "render_type": "CAD material renders",
            "tessellated_parts": len(cache),
            "foreground_metric": "Maximum absolute RGB channel difference from background > 6/255",
            "rgb_variation_metric": "RMS of full-image per-channel standard deviations divided by 255",
            "images": records,
        }
        text = json.dumps(summary, indent=2, allow_nan=False)
        report = stage / "render_validation.json"
        report.write_text(text + "\n", encoding="utf-8")
        for record in records:
            destination = ROOT / record["file"]
            (stage / destination.name).replace(destination)
            if not destination.is_file():
                raise RuntimeError(f"Missing final render: {destination}")
        report.replace(ROOT / report.name)
    print(text, flush=True)


def main():
    if sys.argv[1:] == ["--vtk-worker"]:
        render_all()
        return
    if sys.argv[1:]:
        raise SystemExit("Usage: python render.py")
    result = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()), "--vtk-worker"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"CAD render worker failed with exit code {result.returncode} "
            f"(0x{result.returncode & 0xFFFFFFFF:08X}). See preceding diagnostics. "
            "If VTK terminated natively, verify that its offscreen OpenGL backend and "
            "graphics driver can create a 1400x1000 framebuffer in this session. "
            "No substitute images were generated."
        )


if __name__ == "__main__":
    main()
