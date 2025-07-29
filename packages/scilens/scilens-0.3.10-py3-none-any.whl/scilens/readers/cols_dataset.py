_E='charts'
_D='x_index'
_C='csv_col_index'
_B='curves'
_A=None
import logging
from dataclasses import dataclass,field
from scilens.components.compare_models import CompareGroup
from scilens.components.compare_floats import CompareFloats
from scilens.config.models.reader_format_cols_curve import ReaderCurveParserNameConfig
@dataclass
class ColsDataset:cols_count:int=0;rows_count:int=0;names:list[str]=field(default_factory=lambda:[]);numeric_col_indexes:list[int]=field(default_factory=lambda:[]);data:list[list[float]]=field(default_factory=lambda:[]);origin_line_nb:list[int]=field(default_factory=lambda:[])
@dataclass
class ColsCurves:type:str;info:dict;curves:dict
def cols_dataset_get_curves_col_x(cols_dataset,col_x):
	I='title';B=col_x;A=cols_dataset;E={}
	if isinstance(B,int):
		C=B-1
		if C<0 or C>=A.cols_count:raise Exception('curve parser col_x: col_index is out of range.')
	if isinstance(B,str):B=[B]
	if isinstance(B,list):
		G=[A for(A,C)in enumerate(A.names)if C in B]
		if len(G)==0:return _A,E
		C=G[0]
	E[_D]=C;J=[B for(A,B)in enumerate(A.numeric_col_indexes)if A!=C];F=[];H=[]
	for D in J:B=A.data[C];K=A.data[D];L={I:A.names[D],'short_title':A.names[D],'series':[[B[A],K[A]]for A in range(A.rows_count)],_C:D};F+=[L];M={I:A.names[D],'type':'simple','xaxis':A.names[C],'yaxis':A.names[D],_B:[len(F)-1]};H+=[M]
	return{_B:F,_E:H},E
def compare(group,compare_floats,reader_test,reader_ref,cols_curve):
	O='Errors limit reached';F=reader_ref;D=group;C=cols_curve;A=reader_test;logging.debug(f"compare cols: {D.name}")
	if len(A.numeric_col_indexes)!=len(F.numeric_col_indexes):D.error=f"Number Float columns indexes are different: {len(A.numeric_col_indexes)} != {len(F.numeric_col_indexes)}";return
	E=[''for A in range(A.cols_count)];I=_A;G=_A
	if C and C.type==ReaderCurveParserNameConfig.COL_X:J=C.info[_D];I=A.data[J];G=A.names[J]
	K=False
	for B in range(A.cols_count):
		if B not in A.numeric_col_indexes:continue
		P=A.data[B];Q=F.data[B];logging.debug(f"compare cols: {A.names[B]}");L,R,T=compare_floats.add_group_and_compare_vectors(A.names[B],D,{'info_prefix':G}if G else _A,P,Q,info_vector=I)
		if R:K=True;E[B]=O;continue
		if L.total_errors>0:E[B]=f"{L.total_errors} comparison errors"
	if C:
		for M in C.curves[_E]:
			N=0
			for S in M[_B]:
				H=C.curves[_B][S]
				if E[H[_C]]:H['comparison_error']=E[H[_C]];N+=1
			M['comparison']={'curves_nb_with_error':N}
	D.error=O if K else _A;D.info={'cols_has_error':E}