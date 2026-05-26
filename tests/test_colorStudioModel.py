import sys
import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, mock_open


from src.models.colorStudioModel import (
    Images,
    Light,
    Scene,
    PostProcess,
    Saturation,
    AE_Ymean,
    PPClip
)

class TestColorStudioModel:


    
    @patch('src.models.colorStudioModel.loadImage')
    @patch('src.models.colorStudioModel.printProgressBar')
    def test_images_load(self, mock_progressBar, mock_loadImage):
        mock_loadImage.return_value = np.zeros((2, 2, 3))
        
        imgs = Images("path/", "base", ".jpg", nbImage=3, nbDigit=4, load=True)
        
        # Vérifications
        assert imgs.len() == 3
        assert len(imgs._images) == 3
        assert imgs.isHDR() == False
        assert mock_loadImage.call_count == 3
        np.testing.assert_array_equal(imgs._images[0], np.zeros((2, 2, 3)))

    
    def test_light_initialization(self):
        light = Light("TestLight")
        assert light._name == "TestLight"
        assert light._exposure == 0
        np.testing.assert_array_equal(light._npColorRGB, np.array([1.0, 1.0, 1.0]))
        assert light._needUpdate == False
        assert light._firstUpdate == True

    def test_light_setters_trigger_update(self):
        light = Light()
        
        light.setExposure(1.5)
        assert light._exposure == 1.5
        assert light._needUpdate == True
        
        light._needUpdate = False 
        
        light.setColor(np.array([1.0, 0.0, 0.0]))
        assert light._needUpdate == True

    def test_light_render(self):
        light = Light("RenderLight")
        
        mock_images = MagicMock()
        mock_images._images = [np.full((2, 2, 3), 0.5)]
        
        light.setImagesArray(mock_images)
        light.setImageIdx(0)
        
        light.setExposure(1.0)
        light.setColor(np.array([1.0, 1.0, 1.0]))
        
        rendered_img = light.render()
        
        np.testing.assert_array_equal(rendered_img, np.full((2, 2, 3), 1.0))
        assert light._firstUpdate == False
        assert light._needUpdate == False

        rendered_img_cached = light.render()
        assert rendered_img is rendered_img_cached



    def test_scene_add_and_get_light(self):
        scene = Scene()
        light1 = Light("Lumiere1")
        light2 = Light("Lumiere2")
        
        scene.addLight(light1)
        scene.addLight(light2)
        
        assert len(scene._lights) == 2
        assert scene.getLightByName("Lumiere2") == light2
        assert scene.getLightByName("Inconnu") == None

    def test_scene_render(self):
        scene = Scene(hdr=False)
        
        mock_light1 = MagicMock()
        mock_light1.render.return_value = np.full((2, 2, 3), 0.6)
        mock_light1._ImagesArray._images = [np.zeros((2, 2, 3))]
        
        mock_light2 = MagicMock()
        mock_light2.render.return_value = np.full((2, 2, 3), 0.6)
        
        scene.addLight(mock_light1)
        scene.addLight(mock_light2)
        
        out_img = scene.render()
        
        np.testing.assert_array_equal(out_img, np.full((2, 2, 3), 1.0))



    def test_postprocess_base(self):
        pp = PostProcess()
        img = np.array([1, 2, 3])
        assert pp.postProcess(img) is img

    def test_saturation_postprocess(self):
        sat = Saturation(linearSat=50, gammaSat=0)
        img_mock = np.full((10, 10, 3), 0.5, dtype=np.float32)
        
        img_out = sat.postProcess(img_mock)
        assert img_out.shape == img_mock.shape
        assert img_out.dtype == np.float32

    @patch('src.models.colorStudioModel.image2Ymean')
    def test_aeymean_postprocess(self, mock_image2Ymean):
        mock_image2Ymean.return_value = 0.25 
        
        ae = AE_Ymean(Ytarget=0.5, exposure=0.0)
        img_mock = np.full((2, 2, 3), 0.25) 
        
        img_out = ae.postProcess(img_mock)
        
        np.testing.assert_array_equal(img_out, np.full((2, 2, 3), 0.5))

    def test_ppclip_postprocess(self):
        clip = PPClip(minValue=0.1, maxValue=0.9)
        img_mock = np.array([-1.0, 0.5, 2.0])
        
        img_out = clip.postProcess(img_mock)
        
        np.testing.assert_array_equal(img_out, np.array([0.1, 0.5, 0.9]))