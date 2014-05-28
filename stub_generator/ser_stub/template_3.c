typedef void FN_TYPE, ARG1_T, ARG2_T, ARG3_T;

FN_TYPE __sg_FN_NAME(spdid_t spdid, ARG1_T ARG1_V, ARG2_T ARG2_V, ARG3_T ARG3_V)
{
	FN_TYPE ret;
	ret = FN_NAME(spdid, ARG1_V,  ARG2_V,  ARG3_V);
	return ret;
}
