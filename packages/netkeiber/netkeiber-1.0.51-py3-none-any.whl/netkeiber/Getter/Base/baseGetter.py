from LibHanger.Models.recset import recset
from netkeiber.Library.netkeiberController import netkeibaBrowserController
from netkeiber.Library.netkeiberGlobals import *

class baseGetter(netkeibaBrowserController):
    """
    Getter基底
    """

    __dictResult = {}
    """ 処理結果 """

    def __init__(self) -> None:
        """
        コンストラクタ
        """

        # 基底コンストラクタ
        super().__init__(gv.netkeiberConfig)

        # 処理結果Dict
        self.__dictResult = {}

    @property
    def scrapingCount(self):
        """
        スクレイピング回数
        """

        return (
            self.wdc.browserCtl.loadPageCount if not self.wdc.browserCtl is None else 0
        )

    class getterResult:
        """
        Getter処理結果
        """

        def __init__(self, __recordCount: int, __recSet: recset):
            """
            コンストラクタ

            Parameters
            ----------
            __recordCount : int
                レコード数
            __recSet : recset
                レコードセット
            """

            self.recordCount: int = __recordCount
            """ 取得件数 """

            self.recSet: recset = __recSet
            """ 取得したレコードセット """

    def addResult(self, __key, __recordCount: int, __recSet: recset):
        """
        処理結果追加

        Parameters
        ----------
        __key : Any
            処理結果Key(テーブル名)
        __recordCount : int
            レコード数
        __recSet : recset
            レコードセット
        """

        # 処理結果をdictにセット
        self.__dictResult[__key] = self.getterResult(__recordCount, __recSet)

        # 戻り値を返す
        return self.__dictResult
