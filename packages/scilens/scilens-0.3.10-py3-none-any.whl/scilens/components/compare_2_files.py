import os,re
from scilens.run.task_context import TaskContext
from scilens.readers.reader_interface import ReaderInterface
from scilens.components.file_reader import FileReader
from scilens.components.compare_models import SEVERITY_ERROR
from scilens.components.compare_errors import CompareErrors
from scilens.components.compare_floats import CompareFloats
class Compare2Files:
	def __init__(A,context):A.context=context
	def compare(B,path_test,path_ref):
		W='comparison_errors';V='comparison';S=path_ref;R=path_test;Q='reader';P='skipped';N='error';M=True;L='ref';G='path';F='test';A={F:{},L:{},V:None,W:None};D={F:{G:R},L:{G:S}};O=B.context.config.compare.sources.not_matching_source_ignore_pattern
		for(H,I)in D.items():
			if not I.get(G)or not os.path.exists(I[G]):
				if O:
					if O=='*':A[P]=M;return A
					else:
						X=os.path.basename(S if H==F else R);Y=re.search(O,X)
						if Y:A[P]=M;return A
				A[N]=f"file {H} does not exist";return A
		Z=FileReader(B.context.working_dir,B.context.config.file_reader,B.context.config.readers,config_alternate_path=B.context.origin_working_dir)
		for(H,I)in D.items():D[H][Q]=Z.read(I[G])
		C=D[F][Q];J=D[L][Q]
		if not C or not J:A[P]=M;return A
		A[F]=C.info();A[L]=J.info()
		if C.read_error:A[N]=C.read_error;return A
		K=CompareErrors(B.context.config.compare.errors_limit,B.context.config.compare.ignore_warnings);a=CompareFloats(K,B.context.config.compare.float_thresholds);C.compare(a,J,param_is_ref=M);E=K.root_group;T={'total_diffs':E.total_diffs}
		if E.info:T.update(E.info)
		A[V]=T;A[W]=K.get_data()
		if E.error:A[N]=E.error;return A
		C.close();J.close();U=len(K.errors[SEVERITY_ERROR])
		if U>0:b=f"{U} comparison errors";A[N]=b
		return A