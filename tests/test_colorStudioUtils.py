import pytest
import numpy as np
import math
from unittest.mock import patch

from src.utils.colorStudioUtils import (
    inRange2D,
    image2Ymean,
    imgRGB2chromaRG,
    img2chromaVertices,
    colorWheel,
    printProgressBar,
    loadImage
)

class TestColorStudioUtils:


    def test_inRange2D_inside(self):
        assert inRange2D(pos=(5, 5), orig=(0, 0), size=(10, 10)) == True

    def test_inRange2D_outside(self):
        assert inRange2D(pos=(15, 5), orig=(0, 0), size=(10, 10)) == False

    def test_inRange2D_on_edge(self):
        assert inRange2D(pos=(10, 10), orig=(0, 0), size=(10, 10)) == True
        assert inRange2D(pos=(0, 0), orig=(0, 0), size=(10, 10)) == True


    def test_printProgressBar(self, capsys):
        printProgressBar(iteration=50, total=100, prefix='Progression', suffix='Terminé', length=10)
        captured = capsys.readouterr()
        
        assert 'Progression' in captured.out
        assert 'Terminé' in captured.out
        assert '50.0%' in captured.out
        assert '█████-----' in captured.out 


    def test_image2Ymean(self):
        img_mock = np.full((2, 2, 3), 0.5, dtype=float)
        
        mean_y = image2Ymean(img_mock)
        
        assert isinstance(mean_y, float)
        assert mean_y > 0.0 and mean_y < 1.0

    def test_imgRGB2chromaRG(self):
        img_mock = np.array([
            [[1.0, 0.0, 0.0],  
             [0.0, 1.0, 0.0],  
             [0.0, 0.0, 0.0]]  
        ], dtype=float)

        chroma = imgRGB2chromaRG(img_mock)
        
        assert chroma.shape == (3, 2)
        
        np.testing.assert_array_almost_equal(chroma[0], [1.0, 0.0]) # Rouge pur
        np.testing.assert_array_almost_equal(chroma[1], [0.0, 1.0]) # Vert pur
        np.testing.assert_array_almost_equal(chroma[2], [0.0, 0.0]) # Noir (pas de division par zéro)


    def test_img2chromaVertices_no_scale(self):
        img_mock = np.full((2, 2, 3), 0.5, dtype=float)
        vertices = img2chromaVertices(img_mock, scale=False)
        
        assert vertices.shape == (1, 4, 6)
        
        assert np.all(vertices[:, :, 5] == 1.0)

    def test_img2chromaVertices_with_scale(self):
        img_mock = np.array([
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        ], dtype=float)
        
        vertices = img2chromaVertices(img_mock, scale=True)
        assert vertices.shape == (1, 2, 6)


    def test_colorWheel(self):
        halfSize = 50
        wheel = colorWheel(halfSize)
        
        expected_size = halfSize * 2 + 1
        assert wheel.shape == (expected_size, expected_size, 3)
        
        center_pixel = wheel[halfSize, halfSize]
        assert len(center_pixel) == 3

    @patch('skimage.io.imread')
    def test_loadImage_ldr(self, mock_imread):
        mock_imread.return_value = np.full((10, 10, 3), 127, dtype=np.uint8)
        
        img_loaded = loadImage("fake_image.jpg", scale=1.0)
        
        assert img_loaded.shape == (10, 10, 3)
        assert img_loaded.dtype == np.float64
        assert 0.49 < img_loaded[0, 0, 0] < 0.50

    @patch('imageio.imread')
    @patch('os.path.splitext')
    def test_loadImage_hdr(self, mock_splitext, mock_imageio):
        mock_splitext.return_value = ("fake_image", ".exr")
        
        mock_imageio.return_value = np.full((20, 20, 3), 2.5, dtype=np.float32)
        
        img_loaded = loadImage("fake_image.exr", scale=1.0)
        
        assert img_loaded.shape == (20, 20, 3)
        assert img_loaded.dtype == np.float64
        assert img_loaded[0, 0, 0] == 2.5