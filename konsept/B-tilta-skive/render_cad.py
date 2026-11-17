from pathlib import Path
import math
import vtk
from generate_cad import D

DIR=Path(__file__).resolve().parent/'previews'
DIR.mkdir(exist_ok=True)
COLORS={
 '01_base_casting':'#777573','02_service_hatch':'#a19d97','03_ballast':'#333333',
 '04_pedestal':'#777573','05_hinge_yoke':'#565451','06_pivot_axle_M5':'#bcbab5',
 '08_head_chassis':'#535250','09_canopy_top':'#84807d','10_front_lens':'#ffcf84',
 '11_rear_halo_lens':'#ffbd69','12_recessed_work_lens':'#f3e2c3',
 '13_LED_MCPCB':'#a59e8b','14_ambient_LED_strip':'#ffe4a3',
 '15_battery_pack':'#595f57','16_control_PCB':'#42665a'}

def color(s):
    s=s.lstrip('#')
    return tuple(int(s[i:i+2],16)/255 for i in (0,2,4))

def actor(k, shape, shift=(0,0,0)):
    v,t=shape.tessellate(0.6,0.15)
    pts=vtk.vtkPoints(); pts.SetNumberOfPoints(len(v))
    for i,p in enumerate(v):
        pts.SetPoint(i,p.x+shift[0],p.y+shift[1],p.z+shift[2])
    cells=vtk.vtkCellArray()
    for face in t:
        cells.InsertNextCell(3)
        for p in face: cells.InsertCellPoint(p)
    poly=vtk.vtkPolyData()
    poly.SetPoints(pts);poly.SetPolys(cells)
    norm=vtk.vtkPolyDataNormals();norm.SetInputData(poly);norm.SetFeatureAngle(55);norm.SplittingOff();norm.ConsistencyOn();norm.AutoOrientNormalsOn()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norm.GetOutputPort())
    obj=vtk.vtkActor();obj.SetMapper(mapper)
    cl=COLORS.get(k,'#6e6d69')
    obj.GetProperty().SetColor(*color(cl))
    obj.GetProperty().SetAmbient(.26 if 'lens' not in k else .7)
    obj.GetProperty().SetDiffuse(.72 if 'lens' not in k else .33)
    obj.GetProperty().SetSpecular(.16 if 'lens' not in k else .06)
    obj.GetProperty().SetSpecularPower(25)
    return obj

def render(name, camera, target=(15,0,150), parallel_scale=210, bg=(.009,.009,.009), exploded=False, show_all=False):
    renderer=vtk.vtkRenderer();renderer.SetBackground(*bg)
    window=vtk.vtkRenderWindow();window.SetSize(1500,1050);window.OffScreenRenderingOn();window.SetMultiSamples(4)
    window.AddRenderer(renderer)
    for k,s in D.items():
        if not show_all and k.startswith('17_canopy_M3_'): continue
        shift=(0,0,0)
        if exploded:
            if k=='09_canopy_top': shift=(5,0,95)
            elif k=='08_head_chassis': shift=(0,0,33)
            elif k in ('13_LED_MCPCB','14_ambient_LED_strip'):shift=(0,0,13)
            elif k in ('10_front_lens','11_rear_halo_lens','12_recessed_work_lens'):shift=(0,0,-27)
            elif k=='05_hinge_yoke':shift=(0,-83,0)
            elif k=='06_pivot_axle_M5':shift=(0,-100,0)
            elif k.startswith('07_friction_'): shift=(0,-70,0)
            elif k=='02_service_hatch':shift=(0,0,-48)
            elif k=='03_ballast':shift=(0,0,-26)
            elif k in ('15_battery_pack','16_control_PCB'):shift=(0,0,-12)
        renderer.AddActor(actor(k,s,shift))
    light1=vtk.vtkLight();light1.SetLightTypeToSceneLight();light1.SetPosition(300,-500,650);light1.SetFocalPoint(20,0,170);light1.SetIntensity(1.15);renderer.AddLight(light1)
    light2=vtk.vtkLight();light2.SetLightTypeToSceneLight();light2.SetPosition(-350,250,450);light2.SetFocalPoint(10,0,100);light2.SetIntensity(.65);renderer.AddLight(light2)
    cam=renderer.GetActiveCamera();cam.SetPosition(*camera);cam.SetFocalPoint(*target);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(parallel_scale)
    renderer.ResetCameraClippingRange()
    window.Render()
    filt=vtk.vtkWindowToImageFilter();filt.SetInput(window);filt.SetScale(1);filt.ReadFrontBufferOff();filt.Update()
    w=vtk.vtkPNGWriter();w.SetFileName(str(DIR/name));w.SetInputConnection(filt.GetOutputPort());w.Write()
    print(DIR/name)

render('01_three_quarter.png',(500,-720,310),target=(5,0,132),parallel_scale=190)
render('02_profile.png',(0,-780,195),target=(5,0,125),parallel_scale=160)
render('03_exploded.png',(510,-760,490),target=(4,0,142),parallel_scale=250,exploded=True)
render('04_top.png',(0,-1,900),target=(0,0,150),parallel_scale=185)