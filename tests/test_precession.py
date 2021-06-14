
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')


import pytest
import numpy as np
import precession

#
# def test_silly():
#     """
#     Test the test procedure.
#     """
#
#     assert True



class generictest:
    """
    Parameters
    ----------
    func : function
        The function to test. It should output a single value.
    args : dict
        A dictionary of arguments for func. The keys are the argument names.
        Must be ordered as in the definition of func.
    output_to_compare :
        The value to compare the output to.
    args_to_repeat : list of str (optional)
        Which arguments of func to repeat to get vector output.
    """

    def __init__(self, func, args, output_to_compare, args_to_repeat='all', multiple=2):

        self.func = func
        self.args = args
        self.multiple = multiple
        self.output_to_compare = output_to_compare
        if args_to_repeat == 'all':
            self.args_to_repeat = list(self.args.keys())
        elif args_to_repeat is None:
            self.args_to_repeat = []

    def test_single(self):

        return np.allclose(self.func(**self.args), self.output_to_compare)

    def test_multiple(self):

        _args = self.args.copy()
        for arg in self.args_to_repeat:
            _args[arg] = np.repeat(_args[arg], self.multiple)

        _output_to_compare = np.squeeze(
                                np.repeat(
                                    np.atleast_2d(self.output_to_compare),
                                                  self.multiple, axis=0))

        #assert np.allclose(self.func(**_args), _output_to_compare)
        #return np.allclose(self.func(**_args), _output_to_compare)
        return np.allclose(self.func(**_args), _output_to_compare)

    def __call__(self):
        print
        return self.test_single() and self.test_multiple()


def test_mass1():
    assert generictest(precession.eval_m1,{"q":0.8},[0.55555556])()

def test_mass2():
    assert generictest(precession.eval_m2,{"q":0.8},[0.44444444])()






#
#
# def assert_scalar(testval, func, *args):
#     """
#     Assert that the output of an array is a scalar with correct check value.
#
#     Parameters
#     ----------
#     testval, float:
#         The check value for the function being tested.
#
#     func, function:
#         The function to be tested.
#
#     *args:
#         The parameters passed to func.
#     """
#
#     output = func(*args)
#     # Test scalar input returns scalar output
#     check_scalar = isinstance(output, float)
#     assert check_scalar, 'Scalar input does not return scalar output'
#     # Test function returns correct scalar value
#     check_val = testval == output
#     assert check_val, 'Scalar input returns incorret output value'
#
#
# def assert_vector(testvals, func, *args, shape=None):
#     """
#     Assert that the output of an array is a vector with correct check values.
#
#     Parameters
#     ----------
#     testvals, array:
#         The check values for the function being tested.
#
#     func, function:
#         The function to be tested.
#
#     *args:
#         The parameters passed to func.
#     """
#
#     output = func(*args)
#     # Test vector input returns vector output
#     check_vector = isinstance(output, np.ndarray)
#     assert check_vector, 'Vector input does not return vector output'
#     if shape is not None:
#         check_shape = output.shape == shape
#         assert check_shape, 'Vector input returns incorrect output shape'
#     # Test function returns correct vector values
#     check_vals = (testvals == output).all()
#     assert check_vals, 'Vector input returns incorrect output values'
#
#
# def test_mass1():
#     """
#     Test computation of primary mass.
#     """
#
#     # Test scalar input
#     q = 1.0
#     m1 = 0.5
#     assert_scalar(m1, pre.mass1, q)
#     # Test vector input
#     q = [1.0, 0.0]
#     m1 = [0.5, 1.0]
#     assert_vector(m1, pre.mass1, q)
#
#
# def test_mass2():
#     """
#     Test computation of secondary mass.
#     """
#
#     # Test scalar input
#     q = 1.0
#     m2 = 0.5
#     assert_scalar(m2, pre.mass2, q)
#     # Test vector input
#     q = [1.0, 0.0]
#     m2 = [0.5, 0.0]
#     assert_vector(m2, pre.mass2, q)
#
#
# def test_symmetricmassratio():
#     """
#     Test computation of symmetric mass ratio.
#     """
#
#     # Test scalar input
#     q = 1.0
#     eta = 0.25
#     assert_scalar(eta, pre.symmetricmassratio, q)
#     # Test vector input
#     q = [1.0, 0.0]
#     eta = [0.25, 0.0]
#     assert_vector(eta, pre.symmetricmassratio, q)
#
#
# def test_spin1():
#     """
#     Test computation of primary dimensionless spin.
#     """
#
#     # Test scalar input
#     q = 1.0
#     chi1 = 1.0
#     S1 = 0.25
#     assert_scalar(S1, pre.spin1, q, chi1)
#     # Test vector input
#     #q = [1.0, 0.0]
#     #chi1 = [1.0, 0.0]
#     #q, chi1 = np.meshgrid(q, chi1)
#     #q = q.flatten()
#     #chi1 = chi1.flatten()
#     q = [1.0, 1.0, 0.0, 0.0]
#     chi1 = [1.0, 0.0, 1.0, 0.0]
#     S1 = [0.25, 0.0, 1.0, 0.0]
#     assert_vector(S1, pre.spin1, q, chi1)
#
#
# def test_spin2():
#     """
#     Test computation of secondary dimensionless spin.
#     """
#
#     # Test scalar input
#     q = 1.0
#     chi2 = 1.0
#     S2 = 0.25
#     assert_scalar(S2, pre.spin2, q, chi2)
#     # Test vector input
#     q = [1.0, 1.0, 0.0, 0.0]
#     chi2 = [1.0, 0.0, 1.0, 0.0]
#     S2 = [0.25, 0.0, 0.0, 0.0]
#     assert_vector(S2, pre.spin2, q, chi2)
#
#
# def test_spinmags():
#     """
#     Test computation of dimensionless spins.
#     """
#
#     # Test scalar input
#     q = 1.0
#     chi1 = 1.0
#     chi2 = 1.0
