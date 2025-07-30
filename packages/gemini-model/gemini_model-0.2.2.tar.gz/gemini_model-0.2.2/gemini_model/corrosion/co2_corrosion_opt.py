from gemini_model.model_abstract import Model
from gemini_model.corrosion.correlations_opt.dld_model_opt import DLD
from gemini_model.corrosion.correlations_opt.dlm_model_opt import DLM
from gemini_model.corrosion.correlations_opt.norsok_model_opt import NORSOK


class CO2CorrosionOpt(Model):
    """ Class of DPF

    Class to calculate pressure drop and temperature long the well with multiple sections
    """

    def __init__(self):
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
        self.output = self.calculate_corrosion_rate(u, x)

    def get_output(self):
        """get output of the model"""
        return self.output

    def calculate_corrosion_rate(self, u, x):
        """
          Calculate the corrosion rate.
        """

        model = self.parameters['corrosion_model']

        if model == 'DLD':
            corrosion_model = DLD()
        elif model == "DLM":
            corrosion_model = DLM()
        elif model == 'NORSOK':
            corrosion_model = NORSOK()

        corrosion_model.update_parameters(self.parameters)
        corrosion_model.calculate_output(u, x)
        return corrosion_model.get_output()
