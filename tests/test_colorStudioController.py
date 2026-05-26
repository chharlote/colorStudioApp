import sys
import os
import pytest
from unittest.mock import MagicMock


from src.controllers.colorStudioController import (
    CSController,
    CSLightController,
    CSAEController,
    CSColorWheelController,
    CSSaturationController
)

class TestColorStudioController:


    
    @pytest.fixture
    def mock_root_scene(self):
        """Simule la scène principale (root) qui gère le rendu."""
        root = MagicMock()
        root.render.return_value = "fake_rendered_image"
        return root

    @pytest.fixture
    def mock_widget(self):
        """Simule un widget PyQt qui possède une méthode _update."""
        widget = MagicMock()
        return widget


    def test_light_controller_position_changed(self, mock_root_scene, mock_widget):
        mock_light = MagicMock()
        
        controller = CSLightController(
            root=mock_root_scene, 
            light=mock_light, 
            widget=[mock_widget]
        )
        
        controller.on_position_changed(5)
        
        mock_light.setImageIdx.assert_called_once_with(5)
        mock_root_scene.render.assert_called_once()
        mock_widget._update.assert_called_once_with("fake_rendered_image")

    def test_light_controller_exposure_changed(self, mock_root_scene, mock_widget):
        mock_light = MagicMock()
        
        controller = CSLightController(
            root=mock_root_scene, 
            light=mock_light, 
            widget=[mock_widget]
        )
        
        controller.on_exposure_changed(2.5)
        
        mock_light.setExposure.assert_called_once_with(2.5)
        mock_root_scene.render.assert_called_once()
        mock_widget._update.assert_called_once_with("fake_rendered_image")

    def test_light_controller_color_requested(self, mock_root_scene):
        mock_light = MagicMock()
        mock_light._name = "Light_Test"
        
        mock_cw_controller = MagicMock()
        
        controller = CSLightController(
            root=mock_root_scene, 
            light=mock_light, 
            widget=[], 
            cwController=mock_cw_controller
        )
        
        controller.on_color_requested()
        
        mock_cw_controller._controlledWidget.setWindowTitle.assert_called_once_with("Color Wheel::Light_Test")
        assert mock_cw_controller._scene == mock_light



    def test_ae_controller_exposure_changed(self, mock_root_scene, mock_widget):
        mock_ae = MagicMock()
        
        controller = CSAEController(
            root=mock_root_scene, 
            postprocess=mock_ae, 
            widget=[mock_widget]
        )
        
        controller.on_exposure_changed(-1.0)
        
        mock_ae.setExposure.assert_called_once_with(-1.0)
        mock_root_scene.render.assert_called_once()
        mock_widget._update.assert_called_once_with("fake_rendered_image")



    def test_color_wheel_controller_color_changed(self, mock_root_scene, mock_widget):
        mock_light = MagicMock()
        
        controller = CSColorWheelController(
            root=mock_root_scene, 
            light=mock_light, 
            widget=[mock_widget]
        )
        
        fake_color = (0.5, 0.5, 1.0)
        controller.on_color_changed(fake_color)
        
        mock_light.setColor.assert_called_once_with(fake_color)
        mock_root_scene.render.assert_called_once()
        mock_widget._update.assert_called_once_with("fake_rendered_image")

    def test_color_wheel_controller_no_scene(self, mock_root_scene, mock_widget):
        controller = CSColorWheelController(
            root=mock_root_scene, 
            light=None, 
            widget=[mock_widget]
        )
        
        controller.on_color_changed((1.0, 0.0, 0.0))
        
        mock_root_scene.render.assert_not_called()
        mock_widget._update.assert_not_called()


    def test_saturation_controller_linear_changed(self, mock_root_scene, mock_widget):
        mock_sat = MagicMock()
        
        controller = CSSaturationController(
            root=mock_root_scene, 
            postprocess=mock_sat, 
            widget=[mock_widget]
        )
        
        controller.on_linear_saturation_changed(45)
        
        mock_sat.setLinearSaturation.assert_called_once_with(45)
        mock_root_scene.render.assert_called_once()
        mock_widget._update.assert_called_once_with("fake_rendered_image")

    def test_saturation_controller_gamma_changed(self, mock_root_scene, mock_widget):
        mock_sat = MagicMock()
        
        controller = CSSaturationController(
            root=mock_root_scene, 
            postprocess=mock_sat, 
            widget=[mock_widget]
        )
        
        controller.on_gamma_saturation_changed(-20)
        
        mock_sat.setGammaSaturation.assert_called_once_with(-20)
        mock_root_scene.render.assert_called_once()
        mock_widget._update.assert_called_once_with("fake_rendered_image")