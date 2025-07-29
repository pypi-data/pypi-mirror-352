_A=None
import logging,csv,re
from scilens.readers.reader_interface import ReaderInterface
from scilens.readers.cols_dataset import ColsDataset,ColsCurves,cols_dataset_get_curves_col_x,compare as cols_compare
from scilens.readers.mat_dataset import MatDataset,from_iterator as mat_from_iterator,compare as mat_compare,get_data
from scilens.config.models.reader_format_csv import ReaderCsvConfig,ReaderCsvMatrixConfig
from scilens.config.models.reader_format_cols_curve import ReaderCurveParserNameConfig
from scilens.components.compare_models import CompareGroup
from scilens.components.compare_floats import CompareFloats
def is_num(x):
	try:return float(x)
	except ValueError:return
def csv_row_detect_header(first_row):
	A=first_row
	if all(not A.isdigit()for A in A):return True,A
	else:return False,[f"Column {A}"for(A,B)in enumerate(A)]
def csv_row_detect_cols_num(row):return[A for(A,B)in enumerate(row)if is_num(B)!=_A]
def csv_detect(path,delimiter,quotechar,encoding):
	with open(path,'r',encoding=encoding)as B:A=csv.reader(B,delimiter=delimiter,quotechar=quotechar);C=next(A);D,E=csv_row_detect_header(C);F=next(A);G=csv_row_detect_cols_num(F);return D,E,G
class ReaderCsv(ReaderInterface):
	configuration_type_code='csv';category='datalines';extensions=['CSV']
	def read(A,reader_options):
		B=reader_options;A.reader_options=B;J=B.ignore_lines_patterns;A.raw_lines_number=_A;A.curves=_A;A.report_matrices=_A;D,F,P=csv_detect(A.origin.path,A.reader_options.delimiter,A.reader_options.quotechar,encoding=A.encoding);A.has_header=D;A.cols=F;A.numeric_col_indexes=P
		with open(A.origin.path,'r',encoding=A.encoding)as Q:
			K=Q.readlines();L=csv.reader(K,delimiter=A.reader_options.delimiter,quotechar=A.reader_options.quotechar)
			if B.is_matrix:
				E=B.matrix or ReaderCsvMatrixConfig();G=mat_from_iterator(x_name=E.x_name,y_name=E.y_name,reader=L,has_header=D,x_value_line=E.x_value_line,has_y=E.has_y)
				if E.export_report:A.report_matrices=get_data([G],['csv'])
				A.mat_dataset=G;A.raw_lines_number=G.nb_lines+(1 if D else 0)
			else:
				if B.ignore_columns:
					if not D:raise Exception('Ignore columns is not supported without header.')
					A.numeric_col_indexes=[C for C in A.numeric_col_indexes if A.cols[C]not in B.ignore_columns]
				M=len(F);C=ColsDataset(cols_count=M,names=F,numeric_col_indexes=A.numeric_col_indexes,data=[[]for A in range(M)]);H=0
				for(R,S)in zip(K,L):
					H+=1
					if D and H==1:continue
					if J:
						N=False
						for T in J:
							if bool(re.match(T,R)):N=True;break
						if N:continue
					for(O,I)in enumerate(S):
						if O in C.numeric_col_indexes:I=float(I)
						C.data[O].append(I)
					C.origin_line_nb.append(H)
				C.rows_count=len(C.origin_line_nb);A.cols_dataset=C;A.raw_lines_number=C.rows_count+(1 if D else 0)
				if B.curve_parser:
					if B.curve_parser.name==ReaderCurveParserNameConfig.COL_X:
						A.curves,U=cols_dataset_get_curves_col_x(C,B.curve_parser.parameters.x)
						if A.curves:A.cols_curve=ColsCurves(type=ReaderCurveParserNameConfig.COL_X,info=U,curves=A.curves)
					elif B.curve_parser.name==ReaderCurveParserNameConfig.COLS_COUPLE:raise NotImplementedError('cols_couple not implemented')
					else:raise Exception('Curve parser not supported.')
	def compare(A,compare_floats,param_reader,param_is_ref=True):
		H='node';D=param_is_ref;C=param_reader;B=compare_floats;I=A.reader_options
		if I.is_matrix:E=A.mat_dataset if D else C.mat_dataset;F=A.mat_dataset if not D else C.mat_dataset;J,G=B.compare_errors.add_group(H,'csv matrix');mat_compare(G,B,E,F)
		else:E=A.cols_dataset if D else C.cols_dataset;F=A.cols_dataset if not D else C.cols_dataset;K=A.cols_curve if hasattr(A,'cols_curve')else _A;J,G=B.compare_errors.add_group(H,'csv cols');cols_compare(G,B,E,F,K)
	def class_info(A):return{'cols':A.cols,'raw_lines_number':A.raw_lines_number,'curves':A.curves,'matrices':A.report_matrices}