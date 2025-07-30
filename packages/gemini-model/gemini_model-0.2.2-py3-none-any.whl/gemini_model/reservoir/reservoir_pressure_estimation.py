from gemini_model.model_abstract import Model
import numpy as np


class reservoir_pressure(Model):
    """ Class of reservoir_pressure to estimate reservoir pressure from the slop plot
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

        """ get input where flow and p_bh are the arrays of flow and bottomhole
             pressure values. Using the polynomial fitting, the reservoir
             pressure is estimated.
        """

        flow = u['flow']
        p_bh = u['bottomhole_pressure']

        # Calculate p/Q and 1/Q for regression
        p_over_Q = p_bh / flow
        inv_Q = 1 / flow

        # Linear fit
        fit_params = np.polyfit(inv_Q, p_over_Q, 1)
        fit_function = np.poly1d(fit_params)

        # Calculate R-squared
        residuals = p_over_Q - fit_function(inv_Q)
        ss_residuals = np.sum(residuals**2)
        ss_total = np.sum((p_over_Q - np.mean(p_over_Q))**2)
        r_squared = 1 - (ss_residuals / ss_total)

        res_press = fit_params[0]

        self.output['reservoir_pressure'] = res_press
        self.output['r_squared'] = r_squared

    def get_output(self):
        """get output of the model"""
        return self.output
