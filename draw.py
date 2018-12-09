import vtk
import vtk.util.numpy_support as VN
import numpy as np
import re
from pathlib import Path
from multiprocessing import Pool
from progress.bar import Bar


dataName = "yA31"
dataType = 'tev'
method = 'volume'
# outputDir = "output_"+method+"_"+dataName+"_"+dataType
outputDir = "output_test_3"

def shotFrame(index):
    # This template is going to show a slice of the data

    # the data used in this example can be download from
    # http://oceans11.lanl.gov/deepwaterimpact/yA31/300x300x300-FourScalars_resolution/pv_insitu_300x300x300_49275.vti 

    #setup the dataset filepath (change this file path to where you store the dataset)
    filename = dataName+'/'+str(index)+'.vti'

    #the name of data array which is used in this example
    daryName = dataType  #'v02' 'v03' 'prs' 'tev'

    # for accessing build-in color access
    colors = vtk.vtkNamedColors() 

    # Create the renderer, the render window, and the interactor. The
    # renderer draws into the render window, the interactor enables
    # mouse- and keyboard-based interaction with the data within the
    # render window.
    aRenderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(aRenderer)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Set a background color for the renderer and set the size of the
    # render window.
    aRenderer.SetBackground(51/255, 77/255, 102/255)
    renWin.SetSize(600, 600)

    # data reader
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(filename)
    reader.Update()

    # specify the data array in the file to process
    reader.GetOutput().GetPointData().SetActiveAttribute(daryName, 0)

    # convert the data array to numpy array and get the min and maximum valule
    dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars(daryName))
    dMax = np.amax(dary)
    dMin = np.amin(dary)
    # dRange = dMax - dMin
    print("Data array max: ", np.amax(dary))
    print("Data array min: ", np.amin(dary))

    ########## setup color map ###########
    # Now create a lookup table that consists of the full hue circle
    # (from HSV).
    hueLut = vtk.vtkLookupTable()
    hueLut.SetTableRange(dMin, dMax)
    hueLut.SetHueRange(0.18, 0.68)  #comment these three line to default color map, rainbow
    hueLut.SetSaturationRange(0, 1)
    hueLut.SetValueRange(1, 1)
    hueLut.Build()  # effective built

    # An outline provides context around the data.
    outlineData = vtk.vtkOutlineFilter()
    outlineData.SetInputConnection(reader.GetOutputPort())
    outlineData.Update()

    mapOutline = vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outlineData.GetOutputPort())

    outline = vtk.vtkActor()
    outline.SetMapper(mapOutline)
    outline.GetProperty().SetColor(colors.GetColor3d("Black"))

    if method =="slice":
        ########## create plane (slice)  ###########
        # xy plane
        xyColors = vtk.vtkImageMapToColors()
        xyColors.SetInputConnection(reader.GetOutputPort())
        xyColors.SetLookupTable(hueLut)
        xyColors.Update()

        xy = vtk.vtkImageActor()
        xy.GetMapper().SetInputConnection(xyColors.GetOutputPort())
        xy.SetDisplayExtent(0,300,0,300,150,150) 
        # print(xy.GetDisplayBounds())
        aRenderer.AddActor(xy)

    elif method == "volume":
        ########## create volume rendering  ###########
        # Create transfer mapping scalar value to opacity.
        opacityTransferFunction = vtk.vtkPiecewiseFunction()
        opacityTransferFunction.AddPoint(dMin, 0.0)
        opacityTransferFunction.AddPoint(dMax, 1)
        # opacityTransferFunction.AddPoint(dMin+(dMax-dMin)/3, 0)

        # Create transfer mapping scalar value to color.
        colorTransferFunction = vtk.vtkColorTransferFunction()
        colorTransferFunction.SetColorSpaceToDiverging()
        # colorTransferFunction.SetHSVWrap(False)
        colorTransferFunction.AddRGBPoint(dMin, 0.23, 0.298, 0.75)
        # colorTransferFunction.AddRGBPoint(dMin+(dMax-dMin)/3, 0.865,0.865,0.865)
        colorTransferFunction.AddRGBPoint(dMax, 0.705, 0.02, 0.15)

        
        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(dMin,   0.0)
        volumeGradientOpacity.AddPoint(dMin+(dMax-dMin)*0.6,  0.5)
        volumeGradientOpacity.AddPoint(dMax, 1.0)

        # The property describes how the data will look.
        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(colorTransferFunction)
        volumeProperty.SetScalarOpacity(opacityTransferFunction)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        # volumeProperty.ShadeOn()

        # The mapper / ray cast function know how to render the data.
        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(reader.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()

        # The volume holds the mapper and the property and
        # can be used to position/orient the volume.
        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)
        aRenderer.AddActor(volume)

    
    elif method == 'iso':
        ########## create isosurface  ###########
        iso = vtk.vtkContourFilter()
        iso.SetInputConnection(reader.GetOutputPort())
        iso.SetValue(0, 0.1)

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(iso.GetOutputPort())
        normals.SetFeatureAngle(45)

        isoMapper = vtk.vtkPolyDataMapper()
        isoMapper.SetInputConnection(normals.GetOutputPort())
        isoMapper.ScalarVisibilityOff()

        isoActor = vtk.vtkActor()
        isoActor.SetMapper(isoMapper)
        isoActor.GetProperty().SetColor(colors.GetColor3d("bisque"))
        aRenderer.AddActor(isoActor)


    ############### creat text (index) ############
    timeIndex = vtk.vtkTextActor()
    timeIndex.SetInput(filename[5:10])
    timeIndex.SetDisplayPosition(300,30)
    timeIndex.GetTextProperty().SetFontSize(24)
    timeIndex.GetTextProperty().SetJustificationToCentered()
    timeIndex.GetTextProperty().SetColor(1,0,0)


    # Actors are added to the renderer.
    # aRenderer.AddActor(outline)
    aRenderer.AddActor(timeIndex)

    # It is convenient to create an initial view of the data. The
    # FocalPoint and Position form a vector direction. Later on
    # (ResetCamera() method) this vector is used to position the camera
    # to look at the data in this direction.
    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 1, 0)
    aCamera.SetPosition(0, 0, 1) 
    aCamera.SetFocalPoint(0, 0, 0)
    # aCamera.ComputeViewPlaneNormal()


    # An initial camera view is created.  The Dolly() method moves
    # the camera towards the FocalPoint, thereby enlarging the image.
    aRenderer.SetActiveCamera(aCamera)
    aRenderer.ResetCamera()
    aCamera.Dolly(1.2)


    # Note that when camera movement occurs (as it does in the Dolly()
    # method), the clipping planes often need adjusting. Clipping planes
    # consist of two planes: near and far along the view direction. The
    # near plane clips out objects in front of the plane; the far plane
    # clips out objects behind the plane. This way only what is drawn
    # between the planes is actually rendered.
    aRenderer.ResetCameraClippingRange()

    # Interact with the data.
    renWin.Render()
    iren.Initialize()
    iren.Start()

    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    outputFile = outputDir+"/"+str(index)+".png"

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(outputFile)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()

def processOne(index):
    outputFile = outputDir+"/"+str(index)+".png"
    file = Path(outputFile)
    if not file.is_file():
        try:
            shotFrame(index)
        except:
            print("Error...")

def main():
    p = re.compile(r'http://oceans11.*?\.vti')
    with open(dataName+".html",'r',encoding='utf-8') as html:
        text = html.read()
        indices = []
        for url in p.finditer(text):
            indices.append(url.group(0)[-9:-4])  #url[0] is the match 
        pool = Pool(processes=7)
        bar = Bar('Output: ',max = len(indices))
        for _ in pool.imap(processOne, indices):
            bar.next()
        bar.finish()
            
    




if __name__ == '__main__':
    # main()
    shotFrame('16514')