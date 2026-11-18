import vtk, math, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
(ROOT/'previews').mkdir(exist_ok=True)
COLORS={
'C01_RIB_PETG':(.69,.65,.57),
'C02_BASE_PETG':(.65,.61,.53),
'C03_BOTTOM_PETG':(.60,.57,.50),
'C05_DIFFUSER_OPAL_PC':(1.0,.83,.54),
'C06_DIFFUSER_CAP':(.65,.61,.54),
'C07_UPPER_COLLAR':(.62,.57,.50),
}

def actor(name,angle=0):
    reader=vtk.vtkSTLReader();reader.SetFileName(str(ROOT/'stl'/f'{name}.stl'));reader.Update()
    normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(reader.GetOutputPort());normals.SplittingOff();normals.ConsistencyOn();normals.AutoOrientNormalsOn();normals.Update()
    m=vtk.vtkPolyDataMapper();m.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(m)
    a.GetProperty().SetColor(*COLORS[name]);a.GetProperty().SetAmbient(.30 if 'DIFFUSER' in name else .15);a.GetProperty().SetDiffuse(.76)
    a.GetProperty().SetSpecular(.07);a.GetProperty().SetSpecularPower(20)
    a.RotateZ(angle)
    return a

def render(fn,cam=(5,-700,320), scale=245,background=(0,0,0)):
    ren=vtk.vtkRenderer();ren.SetBackground(*background)
    for key in ['C02_BASE_PETG','C03_BOTTOM_PETG','C05_DIFFUSER_OPAL_PC','C06_DIFFUSER_CAP','C07_UPPER_COLLAR']:
        ren.AddActor(actor(key))
    for k in range(8):ren.AddActor(actor('C01_RIB_PETG',k*45+22.5))
    for pos,power in [((-360,-450,700),1.00),((350,400,400),.46),((-100,450,350),.55)]:
      l=vtk.vtkLight();l.SetLightTypeToSceneLight();l.SetPositional(False);l.SetPosition(*pos);l.SetFocalPoint(0,0,110);l.SetIntensity(power);ren.AddLight(l)
    ren.SetAutomaticLightCreation(False)
    camera=ren.GetActiveCamera();camera.SetPosition(*cam);camera.SetFocalPoint(0,0,114);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(scale/2)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(ren);win.SetSize(1050,1150);win.SetMultiSamples(8)
    win.Render();img=vtk.vtkWindowToImageFilter();img.SetInput(win);img.SetInputBufferTypeToRGB();img.ReadFrontBufferOff();img.Update()
    w=vtk.vtkPNGWriter();w.SetFileName(str(ROOT/'previews'/fn));w.SetInputConnection(img.GetOutputPort());w.Write();win.Finalize()

render('front.png',cam=(0,-700,250),scale=245)
render('threequarter.png',cam=(140,-660,300),scale=245)
render('side.png',cam=(490,-490,270),scale=245)
render('top.png',cam=(.1,-.1,700),scale=250)
