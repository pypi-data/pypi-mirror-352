from funcnodes_basic import math_nodes
import math
import sys
import pytest_funcnodes


@pytest_funcnodes.nodetest(math_nodes.value_node)
async def test_value_node():
    node = math_nodes.value_node()
    node.inputs["value"].value = 10.0
    await node
    assert node.outputs["out"].value == 10.0


@pytest_funcnodes.nodetest(math_nodes.add_node)
async def test_add_node():
    node = math_nodes.add_node()
    node.inputs["a"].value = 3.0
    node.inputs["b"].value = 2.0
    await node
    assert node.outputs["out"].value == 5.0


@pytest_funcnodes.nodetest(math_nodes.sub_node)
async def test_sub_node():
    node = math_nodes.sub_node()
    node.inputs["a"].value = 5.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == 2.0


@pytest_funcnodes.nodetest(math_nodes.mul_node)
async def test_mul_node():
    node = math_nodes.mul_node()
    node.inputs["a"].value = 4.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == 12.0


@pytest_funcnodes.nodetest(math_nodes.div_node)
async def test_div_node():
    node = math_nodes.div_node()
    node.inputs["a"].value = 10.0
    node.inputs["b"].value = 2.0
    await node
    assert node.outputs["out"].value == 5.0


@pytest_funcnodes.nodetest(math_nodes.mod_node)
async def test_mod_node():
    node = math_nodes.mod_node()
    node.inputs["a"].value = 10.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == 1.0


@pytest_funcnodes.nodetest(math_nodes.pow_node)
async def test_pow_node():
    node = math_nodes.pow_node()
    node.inputs["a"].value = 2.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == 8.0


@pytest_funcnodes.nodetest(math_nodes.floor_div_node)
async def test_floor_div_node():
    node = math_nodes.floor_div_node()
    node.inputs["a"].value = 10.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == 3.0


@pytest_funcnodes.nodetest(math_nodes.abs_node)
async def test_abs_node():
    node = math_nodes.abs_node()
    node.inputs["a"].value = -5.0
    await node
    assert node.outputs["out"].value == 5.0


@pytest_funcnodes.nodetest(math_nodes.neg_node)
async def test_neg_node():
    node = math_nodes.neg_node()
    node.inputs["a"].value = 5.0
    await node
    assert node.outputs["out"].value == -5.0


@pytest_funcnodes.nodetest(math_nodes.pos_node)
async def test_pos_node():
    node = math_nodes.pos_node()
    node.inputs["a"].value = -5.0
    await node
    assert node.outputs["out"].value == -5.0


@pytest_funcnodes.nodetest(math_nodes.round_node)
async def test_round_node():
    node = math_nodes.round_node()
    node.inputs["a"].value = 5.5678
    node.inputs["ndigits"].value = 2
    await node
    assert node.outputs["out"].value == 5.57


@pytest_funcnodes.nodetest(math_nodes.greater_node)
async def test_greater_node():
    node = math_nodes.greater_node()
    node.inputs["a"].value = 5.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.greater_equal_node)
async def test_greater_equal_node():
    node = math_nodes.greater_equal_node()
    node.inputs["a"].value = 5.0
    node.inputs["b"].value = 5.0
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.less_node)
async def test_less_node():
    node = math_nodes.less_node()
    node.inputs["a"].value = 3.0
    node.inputs["b"].value = 5.0
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.less_equal_node)
async def test_less_equal_node():
    node = math_nodes.less_equal_node()
    node.inputs["a"].value = 5.0
    node.inputs["b"].value = 5.0
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.equal_node)
async def test_equal_node():
    node = math_nodes.equal_node()
    node.inputs["a"].value = 5.0
    node.inputs["b"].value = 5.0
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.not_equal_node)
async def test_not_equal_node():
    node = math_nodes.not_equal_node()
    node.inputs["a"].value = 5.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.and_node)
async def test_and_node():
    node = math_nodes.and_node()
    node.inputs["a"].value = True
    node.inputs["b"].value = True
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.or_node)
async def test_or_node():
    node = math_nodes.or_node()
    node.inputs["a"].value = True
    node.inputs["b"].value = False
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.xor_node)
async def test_xor_node():
    node = math_nodes.xor_node()
    node.inputs["a"].value = True
    node.inputs["b"].value = False
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.not_node)
async def test_not_node():
    node = math_nodes.not_node()
    node.inputs["a"].value = True
    await node
    assert not node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.math_pi_node)
async def test_math_pi_node():
    node = math_nodes.math_pi_node()
    await node
    assert node.outputs["out"].value == math.pi


@pytest_funcnodes.nodetest(math_nodes.math_e_node)
async def test_math_e_node():
    node = math_nodes.math_e_node()
    await node
    assert node.outputs["out"].value == math.e


@pytest_funcnodes.nodetest(math_nodes.math_tau_node)
async def test_math_tau_node():
    node = math_nodes.math_tau_node()
    await node
    assert node.outputs["out"].value == math.tau


@pytest_funcnodes.nodetest(math_nodes.math_inf_node)
async def test_math_inf_node():
    node = math_nodes.math_inf_node()
    await node
    assert node.outputs["out"].value == math.inf


@pytest_funcnodes.nodetest(math_nodes.math_nan_node)
async def test_math_nan_node():
    node = math_nodes.math_nan_node()
    await node
    assert math.isnan(node.outputs["out"].value)


@pytest_funcnodes.nodetest(math_nodes.math_acos_node)
async def test_math_acos_node():
    node = math_nodes.math_acos_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.acos(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_acosh_node)
async def test_math_acosh_node():
    node = math_nodes.math_acosh_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.acosh(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_asin_node)
async def test_math_asin_node():
    node = math_nodes.math_asin_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.asin(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_asinh_node)
async def test_math_asinh_node():
    node = math_nodes.math_asinh_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.asinh(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_atan_node)
async def test_math_atan_node():
    node = math_nodes.math_atan_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.atan(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_atanh_node)
async def test_math_atanh_node():
    node = math_nodes.math_atanh_node()
    node.inputs["a"].value = 0.5
    await node
    assert node.outputs["out"].value == math.atanh(0.5)


@pytest_funcnodes.nodetest(math_nodes.math_ceil_node)
async def test_math_ceil_node():
    node = math_nodes.math_ceil_node()
    node.inputs["a"].value = 1.2
    await node
    assert node.outputs["out"].value == math.ceil(1.2)


@pytest_funcnodes.nodetest(math_nodes.math_cos_node)
async def test_math_cos_node():
    node = math_nodes.math_cos_node()
    node.inputs["a"].value = 0.0
    await node
    assert node.outputs["out"].value == math.cos(0.0)


@pytest_funcnodes.nodetest(math_nodes.math_cosh_node)
async def test_math_cosh_node():
    node = math_nodes.math_cosh_node()
    node.inputs["a"].value = 0.0
    await node
    assert node.outputs["out"].value == math.cosh(0.0)


@pytest_funcnodes.nodetest(math_nodes.math_degrees_node)
async def test_math_degrees_node():
    node = math_nodes.math_degrees_node()
    node.inputs["a"].value = math.pi
    await node
    assert node.outputs["out"].value == math.degrees(math.pi)


@pytest_funcnodes.nodetest(math_nodes.math_erf_node)
async def test_math_erf_node():
    node = math_nodes.math_erf_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.erf(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_erfc_node)
async def test_math_erfc_node():
    node = math_nodes.math_erfc_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.erfc(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_exp_node)
async def test_math_exp_node():
    node = math_nodes.math_exp_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.exp(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_expm1_node)
async def test_math_expm1_node():
    node = math_nodes.math_expm1_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.expm1(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_fabs_node)
async def test_math_fabs_node():
    node = math_nodes.math_fabs_node()
    node.inputs["a"].value = -1.0
    await node
    assert node.outputs["out"].value == math.fabs(-1.0)


@pytest_funcnodes.nodetest(math_nodes.math_floor_node)
async def test_math_floor_node():
    node = math_nodes.math_floor_node()
    node.inputs["a"].value = 1.7
    await node
    assert node.outputs["out"].value == math.floor(1.7)


@pytest_funcnodes.nodetest(math_nodes.math_gamma_node)
async def test_math_gamma_node():
    node = math_nodes.math_gamma_node()
    node.inputs["a"].value = 5.0
    await node
    assert node.outputs["out"].value == math.gamma(5.0)


@pytest_funcnodes.nodetest(math_nodes.math_lgamma_node)
async def test_math_lgamma_node():
    node = math_nodes.math_lgamma_node()
    node.inputs["a"].value = 5.0
    await node
    assert node.outputs["out"].value == math.lgamma(5.0)


@pytest_funcnodes.nodetest(math_nodes.math_log_node)
async def test_math_log_node():
    node = math_nodes.math_log_node()
    node.inputs["a"].value = math.e
    await node
    assert node.outputs["out"].value == math.log(math.e)


@pytest_funcnodes.nodetest(math_nodes.math_log10_node)
async def test_math_log10_node():
    node = math_nodes.math_log10_node()
    node.inputs["a"].value = 100.0
    await node
    assert node.outputs["out"].value == math.log10(100.0)


@pytest_funcnodes.nodetest(math_nodes.math_log1p_node)
async def test_math_log1p_node():
    node = math_nodes.math_log1p_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value == math.log1p(1.0)


@pytest_funcnodes.nodetest(math_nodes.math_log2_node)
async def test_math_log2_node():
    node = math_nodes.math_log2_node()
    node.inputs["a"].value = 8.0
    await node
    assert node.outputs["out"].value == math.log2(8.0)


@pytest_funcnodes.nodetest(math_nodes.math_modf_node)
async def test_math_modf_node():
    node = math_nodes.math_modf_node()
    node.inputs["a"].value = 3.14
    await node
    assert node.outputs["out"].value == math.modf(3.14)


@pytest_funcnodes.nodetest(math_nodes.math_radians_node)
async def test_math_radians_node():
    node = math_nodes.math_radians_node()
    node.inputs["a"].value = 180.0
    await node
    assert node.outputs["out"].value == math.radians(180.0)


@pytest_funcnodes.nodetest(math_nodes.math_sin_node)
async def test_math_sin_node():
    node = math_nodes.math_sin_node()
    node.inputs["a"].value = 0.0
    await node
    assert node.outputs["out"].value == math.sin(0.0)


@pytest_funcnodes.nodetest(math_nodes.math_sinh_node)
async def test_math_sinh_node():
    node = math_nodes.math_sinh_node()
    node.inputs["a"].value = 0.0
    await node
    assert node.outputs["out"].value == math.sinh(0.0)


@pytest_funcnodes.nodetest(math_nodes.math_sqrt_node)
async def test_math_sqrt_node():
    node = math_nodes.math_sqrt_node()
    node.inputs["a"].value = 4.0
    await node
    assert node.outputs["out"].value == math.sqrt(4.0)


@pytest_funcnodes.nodetest(math_nodes.math_tan_node)
async def test_math_tan_node():
    node = math_nodes.math_tan_node()
    node.inputs["a"].value = 0.0
    await node
    assert node.outputs["out"].value == math.tan(0.0)


@pytest_funcnodes.nodetest(math_nodes.math_tanh_node)
async def test_math_tanh_node():
    node = math_nodes.math_tanh_node()
    node.inputs["a"].value = 0.0
    await node
    assert node.outputs["out"].value == math.tanh(0.0)


@pytest_funcnodes.nodetest(math_nodes.math_exp2_node)
async def test_math_exp2_node():
    node = math_nodes.math_exp2_node()
    node.inputs["a"].value = 3.0
    await node
    assert node.outputs["out"].value == math.exp2(3.0)


@pytest_funcnodes.nodetest(math_nodes.math_cbrt_node)
async def test_math_cbrt_node():
    node = math_nodes.math_cbrt_node()
    node.inputs["a"].value = 27.0
    await node
    assert node.outputs["out"].value == math.cbrt(27.0)


@pytest_funcnodes.nodetest(math_nodes.math_isfinite_node)
async def test_math_isfinite_node():
    node = math_nodes.math_isfinite_node()
    node.inputs["a"].value = 1.0
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.math_isinf_node)
async def test_math_isinf_node():
    node = math_nodes.math_isinf_node()
    node.inputs["a"].value = math.inf
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.math_isnan_node)
async def test_math_isnan_node():
    node = math_nodes.math_isnan_node()
    node.inputs["a"].value = math.nan
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.math_trunc_node)
async def test_math_trunc_node():
    node = math_nodes.math_trunc_node()
    node.inputs["a"].value = 1.7
    await node
    assert node.outputs["out"].value == 1


@pytest_funcnodes.nodetest(math_nodes.math_atan2_node)
async def test_math_atan2_node():
    node = math_nodes.math_atan2_node()
    node.inputs["a"].value = 1.0
    node.inputs["b"].value = 1.0
    await node
    assert node.outputs["out"].value == math.atan2(1.0, 1.0)


@pytest_funcnodes.nodetest(math_nodes.math_copysign_node)
async def test_math_copysign_node():
    node = math_nodes.math_copysign_node()
    node.inputs["a"].value = -1.0
    node.inputs["b"].value = 2.0
    await node
    assert node.outputs["out"].value == 1.0


@pytest_funcnodes.nodetest(math_nodes.math_fmod_node)
async def test_math_fmod_node():
    node = math_nodes.math_fmod_node()
    node.inputs["a"].value = 10.5
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == 1.5


@pytest_funcnodes.nodetest(math_nodes.math_hypot_node)
async def test_math_hypot_node():
    node = math_nodes.math_hypot_node()
    node.inputs["a"].value = 3.0
    node.inputs["b"].value = 4.0
    await node
    assert node.outputs["out"].value == 5.0


@pytest_funcnodes.nodetest(math_nodes.math_pow_node)
async def test_math_pow_node():
    node = math_nodes.math_pow_node()
    node.inputs["a"].value = 2.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == 8.0


@pytest_funcnodes.nodetest(math_nodes.math_remainder_node)
async def test_math_remainder_node():
    node = math_nodes.math_remainder_node()
    node.inputs["a"].value = 10.0
    node.inputs["b"].value = 3.0
    await node
    assert node.outputs["out"].value == math.remainder(10.0, 3.0)


@pytest_funcnodes.nodetest(math_nodes.math_nextafter_node)
async def test_math_nextafter_node():
    node = math_nodes.math_nextafter_node()
    node.inputs["a"].value = 1.0
    node.inputs["b"].value = 2.0
    await node
    assert node.outputs["out"].value == math.nextafter(1.0, 2.0)


@pytest_funcnodes.nodetest(math_nodes.math_isclose_node)
async def test_math_isclose_node():
    node = math_nodes.math_isclose_node()
    node.inputs["a"].value = 3.0
    node.inputs["b"].value = 3.0000000001
    await node
    assert node.outputs["out"].value


@pytest_funcnodes.nodetest(math_nodes.math_factorial_node)
async def test_math_factorial_node():
    node = math_nodes.math_factorial_node()
    node.inputs["a"].value = 5
    await node
    assert node.outputs["out"].value == 120


@pytest_funcnodes.nodetest(math_nodes.math_isqrt_node)
async def test_math_isqrt_node():
    node = math_nodes.math_isqrt_node()
    node.inputs["a"].value = 16
    await node
    assert node.outputs["out"].value == 4


@pytest_funcnodes.nodetest(math_nodes.math_gcd_node)
async def test_math_gcd_node():
    node = math_nodes.math_gcd_node()
    node.inputs["a"].value = 8
    node.inputs["b"].value = 12
    await node
    assert node.outputs["out"].value == 4


@pytest_funcnodes.nodetest(math_nodes.math_comb_node)
async def test_math_comb_node():
    node = math_nodes.math_comb_node()
    node.inputs["a"].value = 5
    node.inputs["b"].value = 2
    await node
    assert node.outputs["out"].value == 10


@pytest_funcnodes.nodetest(math_nodes.math_perm_node)
async def test_math_perm_node():
    node = math_nodes.math_perm_node()
    node.inputs["a"].value = 5
    node.inputs["b"].value = 2
    await node
    assert node.outputs["out"].value == 20


@pytest_funcnodes.nodetest(math_nodes.math_lcm_node)
async def test_math_lcm_node():
    node = math_nodes.math_lcm_node()
    node.inputs["a"].value = 12
    node.inputs["b"].value = 15
    await node
    assert node.outputs["out"].value == 60


@pytest_funcnodes.nodetest(math_nodes.math_ldexp_node)
async def test_math_ldexp_node():
    node = math_nodes.math_ldexp_node()
    node.inputs["a"].value = 0.625
    node.inputs["b"].value = 3
    await node
    assert node.outputs["out"].value == 5.0


@pytest_funcnodes.nodetest(math_nodes.math_fsum_node)
async def test_math_fsum_node():
    node = math_nodes.math_fsum_node()
    node.inputs["a"].value = [0.1, 0.2, 0.3]
    await node
    assert node.outputs["out"].value == math.fsum([0.1, 0.2, 0.3])


@pytest_funcnodes.nodetest(math_nodes.math_prod_node)
async def test_math_prod_node():
    node = math_nodes.math_prod_node()
    node.inputs["a"].value = [1.0, 2.0, 3.0]
    await node
    assert node.outputs["out"].value == math.prod([1.0, 2.0, 3.0])


@pytest_funcnodes.nodetest(math_nodes.math_dist_node)
async def test_math_dist_node():
    node = math_nodes.math_dist_node()
    node.inputs["a"].value = [0.0, 0.0]
    node.inputs["b"].value = [3.0, 4.0]
    await node
    assert node.outputs["out"].value == 5.0


if sys.version_info >= (3, 12):

    @pytest_funcnodes.nodetest(math_nodes.math_sumprod_node)
    async def test_math_sumprod_node():
        node = math_nodes.math_sumprod_node()
        node.inputs["a"].value = [1.0, 2.0]
        node.inputs["b"].value = [3.0, 4.0]
        await node
        assert node.outputs["out"].value == 11.0
