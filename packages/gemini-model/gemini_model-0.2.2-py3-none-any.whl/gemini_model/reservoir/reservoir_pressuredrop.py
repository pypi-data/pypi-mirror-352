from gemini_model.model_abstract import Model
import numpy as np


class bottomhole_skin_dp(Model):
    """ Class of bottomhole_dp to calculate bottomhole pressure drop for
    a given flow rate considering pressure changes due to injection and skin effect
    Reference: Akin, 2019, Geothermal re-injection performance evaluation
        using surveillance analysis methods. Renewable Energy.
        doi: 10.1016/j.renene.2019.02.075
    """

    def __init__(self):
        """ Model initialization
        """
        self.parameters = {}
        self.output = {}

    def update_parameters(self, parameters):
        """ To update model parameters

        Parameters
        ----------
        parameters: dict
            parameters dict as defined by the model
        """
        for key, value in parameters.items():
            self.parameters[key] = value

    def initialize_state(self, x):
        """ generate an initial state based on user parameters """
        pass

    def update_state(self, u, x):
        """update the state based on input u and state x"""
        pass

    def calculate_output(self, u, x):
        """calculate output based on input u and state x"""

        # constant
        g = 9.81

        # get input
        flow = u['flow']
        viscosity = u['viscosity']
        density = u['density']
        well_radius = u['well_radius']
        skin_factor = u['skin_factor']

        reservoir_pressure = self.parameters['reservoir_pressure']
        reservoir_radius = self.parameters['reservoir_radius']
        reservoir_permeability = self.parameters['reservoir_permeability']
        reservoir_thickness = self.parameters['reservoir_thickness']
        reservoir_top = self.parameters['reservoir_top']

        deltaP_flow = (
            flow * viscosity * np.log(reservoir_radius / well_radius)
        ) / (
            2 * np.pi * reservoir_permeability * reservoir_thickness
        )

        deltaP_skin = (
            flow * viscosity * skin_factor
        ) / (
            2 * np.pi * reservoir_permeability * reservoir_thickness
        )

        deltaP_HH = reservoir_top * density * g

        self.output['Hydrostatic_dp'] = deltaP_HH
        self.output['skin_dp'] = deltaP_skin
        self.output['bottomhole_dp'] = deltaP_flow
        self.output['reservoir_dp'] = reservoir_pressure + deltaP_flow + deltaP_skin

    def get_output(self):
        """get output of the model"""
        return self.output
