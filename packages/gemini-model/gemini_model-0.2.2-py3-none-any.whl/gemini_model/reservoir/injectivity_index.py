from gemini_model.model_abstract import Model


class injectivity_index(Model):
    """ Class of injectivity_index

        Class to calculate injectivity index
        Reference: R. Arnold, Analytics-Driven Method for
        Injectivity Analysis in Tight and Heterogeneous Waterflooded Reservoir,
          2021, Proceedings joint convention Bandung.
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
        # get input
        flow = u['flow']
        p_bh = u['bottomhole_pressure']

        delta_P = p_bh - self.parameters['reservoir_pressure']
        II = flow / delta_P

        self.output['injectivity_index'] = II

    def get_output(self):
        """get output of the model"""
        return self.output
