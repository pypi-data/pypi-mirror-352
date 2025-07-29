import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class viw_raceid_record_count(Base):
	
	# テーブル名
	__tablename__ = 'viw_raceid_record_count'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	open_year = fld.NumericFields(4,0,primary_key=True,default=0)
	race_count_jra = fld.NumericFields(4,0,default=0)
	race_count_nkaz = fld.NumericFields(4,0,default=0)
