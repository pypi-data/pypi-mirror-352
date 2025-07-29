_E='ref'
_D='test'
_C='name'
_B=None
_A='path'
import logging,os
from scilens.run.task_context import TaskContext
from scilens.components.compare_2_files import Compare2Files
def list_dir(path,filename_match_ignore,recursive,exclude_filepaths=_B):
	I=exclude_filepaths;H=filename_match_ignore;G='rel_path';F='filename_clean';B='';A=path
	if recursive:
		C=[]
		for(D,L,K)in os.walk(A):
			for J in K:C.append({_A:os.path.join(D,J),F:J.replace(str(H),B),G:D.replace(A+os.path.sep,B)if D!=A else B})
		E={os.path.join(A[G],A[F]):A for A in C}
	else:C={C.replace(str(H),B):C for C in os.listdir(A)if os.path.isfile(os.path.join(A,C))};E={C:{_A:os.path.join(A,D),F:C,G:B}for(C,D)in C.items()}
	return{B:A for(B,A)in E.items()if A[_A]not in I}if I else E
class CompareFolders:
	def __init__(A,context):
		C=context;A.context=C;B=C.config.compare.sources;A.cfg=B;A.test_base=os.path.join(C.working_dir,B.test_folder_relative_path);A.ref_base=os.path.join(C.working_dir,B.reference_folder_relative_path)
		if B.additional_path_suffix:A.test=os.path.join(A.test_base,B.additional_path_suffix);A.ref=os.path.join(A.ref_base,B.additional_path_suffix)
		else:A.test=A.test_base;A.ref=A.ref_base
	def compute_list_filenames(A):
		logging.info(f"Comparing folders content: test vs reference");logging.debug(f"Comparing folders content: {A.test} vs {A.ref}");E=[A.context.config_file]if A.context.config_file else _B;F=[]
		if A.test!=A.ref:
			logging.info(f"Listing files in test folder");logging.debug(f"-- test folder: {A.test}");C=list_dir(A.test,A.cfg.test_filename_match_ignore,A.cfg.recursive,exclude_filepaths=E);logging.info(f"Listing files in reference folder");logging.debug(f"-- test reference: {A.ref}");D=list_dir(A.ref,A.cfg.reference_filename_match_ignore,A.cfg.recursive,exclude_filepaths=E);G=sorted(list(set(C.keys())|set(D.keys())))
			for B in G:F.append({_C:B,_D:C[B][_A]if C.get(B)else _B,_E:D[B][_A]if D.get(B)else _B})
		return F
	def compute_comparison(E,items):
		C='error';D=[]
		for B in items:
			logging.info(f"Comparing file: {B[_C]}")
			try:A=Compare2Files(E.context).compare(B[_D],B[_E])
			except Exception as F:A={C:str(F),_D:{},_E:{}}
			A[_C]=B[_C];D.append(A)
			if A.get(C):
				logging.warning(f"Error found in comparison: {A[C]}")
				if A[C]=='No reader found':logging.warning(f"Maybe Config Options could used to derive the correct reader or skip the file");logging.warning(f" - file_reader.extension_unknown_ignore to skip");logging.warning(f" - file_reader.extension_fallback to use a default reader");logging.warning(f" - file_reader.extension_mapping to map extensions")
		return D