typedef void FUNC_TYPE, FUNC_NAME, ARG1_TYPE, ARG1_VAL;

CSTUB_FN_ARGS_1(FUNC_TYPE FN_TYPE, FUNC_NAME FN_NAME, 
		ARG1_TYPE ARG1_T, ARG1_VAL ARG1_V)
{

	CSTUB_ASM_1(FUNC_N, ARG1_V);
	
	CSTUB_POST;
}
