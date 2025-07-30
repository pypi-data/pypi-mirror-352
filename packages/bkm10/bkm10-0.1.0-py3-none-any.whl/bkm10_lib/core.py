# core.py

from bkm10_lib.validation import validate_configuration

from bkm10_lib.formalism import BKMFormalism

import numpy as np

import matplotlib.pyplot as plt

class DifferentialCrossSection:
    """
    Welcome to the `DifferentialCrossSection` class!

    ## Description:
    Compute BKM10 differential cross sections using user-defined inputs.

    ## Parameters
    configuration : dict
        A dictionary containing the configuration settings with the following keys:
        
        - "kinematics" : BKM10Inputs
            Dataclass containing the required kinematic variables.
        
        - "cff_inputs" : Any
            Object or dictionary containing Compton Form Factor values or parameters.
        
        - "target_polarization" : float
            Polarization value for the target (e.g., 0 for unpolarized).
        
        - "lepton_beam_polarization" : float
            Polarization of the lepton beam (e.g., +1 or -1).

    verbose : bool
        A boolean flag that will tell the class to print out various messages at
        intermediate steps in the calculation. Useful if you want to determine when
        you have, say, calculated a given coefficient, like C_{++}^{LP}(n = 1).
    
    debugging : bool
        A boolean flag that will bomb anybody's terminal with output. As the flag is
        entitled, DO NOT USE THIS unless you need to do some serious debugging. We are
        talking about following how the data gets transformed through every calculation.
    """

    def __init__(self, configuration = None, verbose = False, debugging = False):
        
        # (X): Obtain a True/False to operate the calculation in:
        self.configuration_mode = configuration is not None

        # (X): Determine verbose mode:
        self.verbose = verbose

        # (X): Determine debugging mode (DO NOT TURN ON!):
        self.debugging = debugging

        # (X): A dictionary of *every coefficient* that we computed:
        self.coefficients = {}

        # (X): The Trento Angle convention basically shifts all phi to pi - phi:
        self._using_trento_angle_convention = True

        # (X): Hidden data that says if configuration passed:
        self._passed_configuration = False

        # (X): Hidden data that tells us if the functions executed correctly:
        self._evaluated = False

        if verbose:
            print("> [VERBOSE]: Verbose mode on.")
        if debugging:
            print("> [DEBUGGING]: Debugging mode is on — DO NOT USE THIS!")

        if configuration:
            if verbose:
                print("> [VERBOSE]: Configuration dictionary received!")
            if debugging:
                print("> [DEBUGGING]:Configuration dictionary received:\n{configuration}")

            try:
                if debugging:
                    print("> [DEBUGGING]: Trying to initialize configuration...")
            
                # (X): Initialize the class from the dictionary:
                self._initialize_from_config(configuration)

                if debugging:
                    print("> [DEBUGGING]: Configuration passed!")

            except:
                raise Exception("> Unable to initialize configuration!")
            
            self._passed_configuration = True

            if verbose:
                print("> [VERBOSE]: Configuration succeeded!")
            if debugging:
                print(f"> [DEBUGGING]: Configuration succeeded! Now set internal attribute: {self._passed_configuration}")

    @staticmethod
    def _set_plot_style():
        
        plt.rcParams.update({
            "text.usetex": True,
            "font.family": "serif",
        })

        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['xtick.major.size'] = 5
        plt.rcParams['xtick.major.width'] = 0.5
        plt.rcParams['xtick.minor.size'] = 2.5
        plt.rcParams['xtick.minor.width'] = 0.5
        plt.rcParams['xtick.minor.visible'] = True
        plt.rcParams['xtick.top'] = True    

        # Set y axis
        plt.rcParams['ytick.direction'] = 'in'
        plt.rcParams['ytick.major.size'] = 5
        plt.rcParams['ytick.major.width'] = 0.5
        plt.rcParams['ytick.minor.size'] = 2.5
        plt.rcParams['ytick.minor.width'] = 0.5
        plt.rcParams['ytick.minor.visible'] = True
        plt.rcParams['ytick.right'] = True

    def _initialize_from_config(self, configuration_dictionary: dict):
        try:

            # (X): Pass the dictionary into the validation function:
            validated_configuration_dictionary = validate_configuration(configuration_dictionary, self.verbose)

            self.kinematic_inputs = validated_configuration_dictionary["kinematics"]

            self.cff_inputs = validated_configuration_dictionary["cff_inputs"]

            self.target_polarization = validated_configuration_dictionary["target_polarization"]

            self.lepton_polarization = validated_configuration_dictionary["lepton_beam_polarization"]

            self.using_ww = validated_configuration_dictionary["using_ww"]

            self.formalism_plus = self._build_formalism_with_polarization(+1.0)
            
            self.formalism_minus = self._build_formalism_with_polarization(-1.0)

        except Exception as error:

            # (X): Too general, yes, but not sure what we put here yet:
            raise Exception("> Error occurred during validation...") from error
        
    def _build_formalism_with_polarization(self, lepton_polarization: float) -> BKMFormalism:
        return BKMFormalism(
            inputs = self.kinematic_inputs,
            cff_values = self.cff_inputs,
            lepton_polarization = lepton_polarization,
            target_polarization = self.target_polarization,
            using_ww = self.using_ww,
            verbose = self.verbose,
            debugging = self.debugging)
        
    def compute_prefactor(self) -> float:
        """
        Later!
        """
        return self.formalism_plus.compute_cross_section_prefactor()
        
    def compute_c0_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        """
        # if not hasattr(self, "formalism"):
        #     raise RuntimeError("> Formalism not initialized. Make sure configuration is valid.")

        if self.lepton_polarization == 0.:
            return 0.5 * (self.formalism_plus.compute_c0_coefficient(phi_values) + self.formalism_minus.compute_c0_coefficient(phi_values))

        elif self.lepton_polarization == 1.0:
            return self.formalism_plus.compute_c0_coefficient(phi_values)
        
        elif self.lepton_polarization == -1.0:
            return self.formalism_minus.compute_c0_coefficient(phi_values)
    
    def compute_c1_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        """
        # if not hasattr(self, "formalism"):
        #     raise RuntimeError("> Formalism not initialized. Make sure configuration is valid.")

        if self.lepton_polarization == 0.:
            return 0.5 * (self.formalism_plus.compute_c1_coefficient(phi_values) + self.formalism_minus.compute_c1_coefficient(phi_values))

        elif self.lepton_polarization == 1.0:
            return self.formalism_plus.compute_c1_coefficient(phi_values)
        
        elif self.lepton_polarization == -1.0:
            return self.formalism_minus.compute_c1_coefficient(phi_values)
    
    def compute_c2_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        """
        # if not hasattr(self, "formalism"):
        #     raise RuntimeError("> Formalism not initialized. Make sure configuration is valid.")

        if self.lepton_polarization == 0.:
            return 0.5 * (self.formalism_plus.compute_c2_coefficient(phi_values) + self.formalism_minus.compute_c2_coefficient(phi_values))

        elif self.lepton_polarization == 1.0:
            return self.formalism_plus.compute_c2_coefficient(phi_values)
        
        elif self.lepton_polarization == -1.0:
            return self.formalism_minus.compute_c2_coefficient(phi_values)
    
    def compute_c3_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        """
        # if not hasattr(self, "formalism"):
        #     raise RuntimeError("> Formalism not initialized. Make sure configuration is valid.")

        if self.lepton_polarization == 0.:
            return 0.5 * (self.formalism_plus.compute_c3_coefficient(phi_values) + self.formalism_minus.compute_c3_coefficient(phi_values))

        elif self.lepton_polarization == 1.0:
            return self.formalism_plus.compute_c3_coefficient(phi_values)
        
        elif self.lepton_polarization == -1.0:
            return self.formalism_minus.compute_c3_coefficient(phi_values)
    
    def compute_s1_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        """
        # if not hasattr(self, "formalism"):
        #     raise RuntimeError("> Formalism not initialized. Make sure configuration is valid.")

        if self.lepton_polarization == 0.:
            return 0.5 * (self.formalism_plus.compute_s1_coefficient(phi_values) + self.formalism_minus.compute_s1_coefficient(phi_values))

        elif self.lepton_polarization == 1.0:
            return self.formalism_plus.compute_s1_coefficient(phi_values)
        
        elif self.lepton_polarization == -1.0:
            return self.formalism_minus.compute_s1_coefficient(phi_values)
        
    def compute_s2_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        """
        # if not hasattr(self, "formalism"):
        #     raise RuntimeError("> Formalism not initialized. Make sure configuration is valid.")

        if self.lepton_polarization == 0.:
            return 0.5 * (self.formalism_plus.compute_s2_coefficient(phi_values) + self.formalism_minus.compute_s2_coefficient(phi_values))

        elif self.lepton_polarization == 1.0:
            return self.formalism_plus.compute_s2_coefficient(phi_values)
        
        elif self.lepton_polarization == -1.0:
            return self.formalism_minus.compute_s2_coefficient(phi_values)
    
    def compute_s3_coefficient(self, phi_values: np.ndarray) -> np.ndarray:
        """
        """
        # if not hasattr(self, "formalism"):
        #     raise RuntimeError("> Formalism not initialized. Make sure configuration is valid.")
        
        if self.lepton_polarization == 0.:
            return 0.5 * (self.formalism_plus.compute_s3_coefficient(phi_values) + self.formalism_minus.compute_s3_coefficient(phi_values))

        elif self.lepton_polarization == 1.0:
            return self.formalism_plus.compute_s3_coefficient(phi_values)
        
        elif self.lepton_polarization == -1.0:
            return self.formalism_minus.compute_s3_coefficient(phi_values)

    def compute_cross_section(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the four-fold *differential cross-section* as 
        described with the BKM10 Formalism.

        ## Arguments:
        
        phi: np.ndarray
            A NumPy array that will be plugged-and-chugged into the BKM10 formalism.
        """

        # (X): If  the user has not filled in the class inputs...
        if not hasattr(self, 'kinematic_inputs'):

            # (X): ...enforce the class to use this setting:
            raise RuntimeError("> Missing 'kinematic_inputs' configuration before evaluation.")

        # (X): If the user wants some confirmation that stuff is good...
        if self.verbose:

            # (X): ... we simply evaluate the length of the phi array:
            print(f"> [VERBOSE]: Evaluating cross-section at {len(phi_values)} phi points.")

        # (X): If the user wants to see everything...
        if self.debugging:

            # (X): ... we give it to them:
            print(f"> [DEBUGGING]: Evaluating cross-section with phi values of:\n> {phi_values}")

        # (X): Remember what the Trento angle convention is...
        if self._using_trento_angle_convention:

            # (X): ...if it's on, we apply the shift to the angle array:
            verified_phi_values = np.pi - np.atleast_1d(phi_values)

        # (X): Otherwise...
        else:

            # (X): ... just verify that the array of angles is at least 1D:
            verified_phi_values = np.atleast_1d(phi_values)

        # (X): Obtain the cross-section prefactor:
        cross_section_prefactor = self.compute_prefactor()

        # (X): Obtain coefficients:
        coefficient_c_0 = self.compute_c0_coefficient(verified_phi_values)
        coefficient_c_1 = self.compute_c1_coefficient(verified_phi_values)
        coefficient_c_2 = self.compute_c2_coefficient(verified_phi_values)
        coefficient_c_3 = self.compute_c3_coefficient(verified_phi_values)
        coefficient_s_1 = self.compute_s1_coefficient(verified_phi_values)
        coefficient_s_2 = self.compute_s2_coefficient(verified_phi_values)
        coefficient_s_3 = self.compute_s3_coefficient(verified_phi_values)

        # (X): Compute the dfferential cross-section:
        differential_cross_section = .389379 * 1000000. * (cross_section_prefactor * (
            coefficient_c_0 * np.cos(0. * verified_phi_values) + 
            coefficient_c_1 * np.cos(1. * verified_phi_values) +
            coefficient_c_2 * np.cos(2. * verified_phi_values) +
            coefficient_c_3 * np.cos(3. * verified_phi_values) +
            coefficient_s_1 * np.sin(1. * verified_phi_values) + 
            coefficient_s_2 * np.sin(2. * verified_phi_values) +
            coefficient_s_3 * np.sin(3. * verified_phi_values)))
        
        # (X): Store cross-section data as class attribute:
        self.cross_section_values = differential_cross_section

        # (X): The class has now evaluated:
        self._evaluated = True

        # (X): Return the cross section:
        return differential_cross_section
    
    def compute_bsa(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        We compute the BKM-predicted BSA.

        ## Arguments:
        
        phi: np.ndarray
            A NumPy array that will be plugged-and-chugged into the BKM10 formalism.
        """

        # (X): If  the user has not filled in the class inputs...
        if not hasattr(self, 'kinematic_inputs'):

            # (X): ...enforce the class to use this key:
            raise RuntimeError("> Missing 'kinematic_inputs' configuration before evaluation.")

        # (X): If the user wants some confirmation that stuff is good...
        if self.verbose:

            # (X): ... we simply evaluate the length of the phi array:
            print(f"> [VERBOSE]: Evaluating cross-section at {len(phi_values)} phi points.")

        # (X): If the user wants to see everything...
        if self.debugging:

            # (X): ... we give it to them:
            print(f"> [DEBUGGING]: Evaluating cross-section with phi values of:\n> {phi_values}")

        # (X): Remember what the Trento angle convention is...
        if self._using_trento_angle_convention:

            # (X): ...if it's on, we apply the shift to the angle array:
            verified_phi_values = np.pi - np.atleast_1d(phi_values)

        # (X): Otherwise...
        else:

            # (X): ... just verify that the array of angles is at least 1D:
            verified_phi_values = np.atleast_1d(phi_values)

        # (X): Compute the differential cross-section according to lambda = +1.0:
        sigma_plus = (
            self.formalism_plus.compute_c0_coefficient(verified_phi_values) * np.cos(0. * verified_phi_values)
            + self.formalism_plus.compute_c1_coefficient(verified_phi_values) * np.cos(1. * verified_phi_values)
            + self.formalism_plus.compute_c2_coefficient(verified_phi_values) * np.cos(2. * verified_phi_values)
            + self.formalism_plus.compute_c3_coefficient(verified_phi_values) * np.cos(3. * verified_phi_values)
            + self.formalism_plus.compute_s1_coefficient(verified_phi_values) * np.sin(1. * verified_phi_values)
            + self.formalism_plus.compute_s2_coefficient(verified_phi_values) * np.sin(2. * verified_phi_values)
            + self.formalism_plus.compute_s3_coefficient(verified_phi_values) * np.sin(3. * verified_phi_values)
            )
    
        # (X): Compute the differential cross-section according to lambda = +1.0:
        sigma_minus = (
            self.formalism_minus.compute_c0_coefficient(verified_phi_values) * np.cos(0. * verified_phi_values)
            + self.formalism_minus.compute_c1_coefficient(verified_phi_values) * np.cos(1. * verified_phi_values)
            + self.formalism_minus.compute_c2_coefficient(verified_phi_values) * np.cos(2. * verified_phi_values)
            + self.formalism_minus.compute_c3_coefficient(verified_phi_values) * np.cos(3. * verified_phi_values)
            + self.formalism_minus.compute_s1_coefficient(verified_phi_values) * np.sin(1. * verified_phi_values)
            + self.formalism_minus.compute_s2_coefficient(verified_phi_values) * np.sin(2. * verified_phi_values)
            + self.formalism_minus.compute_s3_coefficient(verified_phi_values) * np.sin(3. * verified_phi_values)
            )

        # (X): Compute the numerator of the BSA: sigma(+) - sigma(-):
        numerator = sigma_plus - sigma_minus

        # (X): Compute the denominator of the BSA: sigma(+) + sigma(-):
        denominator = sigma_plus + sigma_minus

        # (X): Compute the dfferential cross-section:
        bsa_values = numerator / denominator
        
        # (X): Store cross-section data as class attribute:
        self.bsa_values = bsa_values

        # (X): Return the cross section:
        return bsa_values
    
    def get_coefficient(self, name: str) -> np.ndarray:
        """
        ## Description:
        An interface to query a given BKM coefficient
        """

        # (X): ...
        if not self._evaluated:

            # (X): ...
            raise RuntimeError("Call `evaluate(phi)` first before accessing coefficients.")
        
        # (X): In case there is an issue:
        try:
            
            # (X): Return the coefficient:
            return self.coefficients.get(name, None)
        
        # (X): Catch general exceptions:
        except Exception as exception:

            # (X): Raise an error:
            raise NotImplementedError(f"> Something bad happened...: {exception}")
        
    def plot_cross_section(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        Plot the four-fold differential cross-section as a function of azimuthal angle φ.

        ## Arguments:
        phi_values : np.ndarray
            Array of φ values (in degrees) at which to compute and plot the cross-section.
        """

        # (X): We need to check if the cross-section has been evaluated yet:
        if not self._evaluated:
            if self.verbose:
                print("> [VERBOSE]: No precomputed cross-section found. Computing now...")
            if self.debugging:
                print("> [DEBUGGING]: No precomputed cross-section found. Computing now...")

            self.cross_section_values = self.compute_cross_section(phi_values)

        else:
            if self.verbose:
                print("> [VERBOSE]: Found cross-section data... Now constructing plots.")

        self._set_plot_style()

        cross_section_figure_instance, cross_section_axis_instance = plt.subplots(figsize = (8, 5))

        cross_section_axis_instance.plot(phi_values, self.cross_section_values, color = 'black')
        cross_section_axis_instance.set_xlabel(r"Azimuthal Angle $\phi$ (degrees)", fontsize = 14)
        cross_section_axis_instance.set_ylabel(r"$\frac{d^4\sigma}{dQ^2 dx_B dt d\phi}$ (nb/GeV$^4$)", fontsize = 14)
        cross_section_axis_instance.grid(True)
        # cross_section_axis_instance.legend(fontsize = 12)

        try:
            kinematics = self.kinematic_inputs

            title_string = (
                rf"$Q^2 = {kinematics.squared_Q_momentum_transfer:.2f}$ GeV$^2$, "
                rf"$x_B = {kinematics.x_Bjorken:.2f}$, "
                rf"$t = {kinematics.squared_hadronic_momentum_transfer_t:.2f}$ GeV$^2$, "
                rf"$k = {kinematics.lab_kinematics_k:.2f}$ GeV"
                )
            
            cross_section_axis_instance.set_title(title_string, fontsize = 14)

        except AttributeError:

            if self.verbose:
                print("> [VERBOSE]: Could not find full kinematics for title.")

            cross_section_axis_instance.set_title(r"Differential Cross Section vs. $\phi$", fontsize = 14)

        plt.tight_layout()
        plt.show()

    def plot_bsa(self, phi_values: np.ndarray) -> np.ndarray:
        """
        ## Description:
        Plot the BKM-predicted BSA with azimuthal angle φ.

        ## Arguments:
        phi_values : np.ndarray
            Array of φ values (in degrees) at which to compute and plot the cross-section.
        """

        # (X): We need to check if the cross-section has been evaluated yet:
        if not self._evaluated:
            if self.verbose:
                print("> [VERBOSE]: No precomputed cross-section found. Computing now...")

            if self.debugging:
                print("> [DEBUGGING]: No precomputed cross-section found. Computing now...")

            self.bsa_values = self.compute_bsa(phi_values)

        else:
            if self.verbose:
                print("> [VERBOSE]: Found cross-section data... Now constructing plots.")

        self._set_plot_style()

        bsa_figure_instance, bsa_axis_instance = plt.subplots(figsize = (8, 5))

        bsa_axis_instance.plot(
            phi_values,
            self.bsa_values,
            color = 'black')
        bsa_axis_instance.set_xlabel(
            r"Azimuthal Angle $\phi$ (degrees)",
            fontsize = 14)
        bsa_axis_instance.set_ylabel(
            r"$\frac{d^4\sigma \left( \lambda = +1 \right) - d^4\sigma \left( \lambda = -1 \right)}{d^4\sigma \left( \lambda = +1 \right) + d^4\sigma \left( \lambda = -1 \right)}$ (unitless)",
            fontsize = 14)
        bsa_axis_instance.grid(True)

        try:
            kinematics = self.kinematic_inputs

            title_string = (
                rf"$Q^2 = {kinematics.squared_Q_momentum_transfer:.2f}$ GeV$^2$, "
                rf"$x_B = {kinematics.x_Bjorken:.2f}$, "
                rf"$t = {kinematics.squared_hadronic_momentum_transfer_t:.2f}$ GeV$^2$, "
                rf"$k = {kinematics.lab_kinematics_k:.2f}$ GeV"
                )
            
            bsa_axis_instance.set_title(f"BSA for {title_string}", fontsize = 14)

        except AttributeError:

            if self.verbose:
                print("> [VERBOSE]: Could not find full kinematics for title.")

            bsa_axis_instance.set_title(r"BSA vs. $\phi$", fontsize = 14)

        plt.tight_layout()
        plt.show()