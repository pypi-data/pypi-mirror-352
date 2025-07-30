import pandas as pd
import httpx
from io import BytesIO
import logging
from pathlib import Path
from typing import Tuple, Optional
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('SZSE_Stock_Fetcher')

#### 深交所股票列表获取类 ####
# 该类负责从深交所获取股票列表数据，并进行解析和清理
class SZSEFetcher:
    """
    从深交所获取股票列表的类
    
    功能：
    - 下载深交所股票列表XLSX文件
    - 解析表格数据
    - 清理和标准化股票数据
    """
    
    BASE_URL = "https://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1"
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.Client(
            headers=self.DEFAULT_HEADERS,
            timeout=self.timeout,
            follow_redirects=True,
            http2=True
        )
    
    def download_stock_list(self) -> Optional[bytes]:
        """
        下载深交所股票列表数据
        
        返回:
            bytes - 二进制文件内容，或None表示失败
        """
        logger.info("开始下载深交所股票列表")
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.get(self.BASE_URL)
                response.raise_for_status()
                
                if b"Error in getting data" in response.content:
                    logger.error("服务端返回了错误内容")
                    return None
                    
                logger.info(f"成功下载股票列表 - 大小: {len(response.content)} 字节")
                return response.content
                
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP错误 (尝试 {attempt+1}/{self.max_retries}): {e}")
            except httpx.TimeoutException:
                logger.warning(f"请求超时 (尝试 {attempt+1}/{self.max_retries})")
            except httpx.RequestError as e:
                logger.error(f"网络连接错误: {str(e)}")
        
        logger.error(f"经过 {self.max_retries} 次尝试后下载失败")
        return None

    def parse_stock_list(self, content: bytes) -> pd.DataFrame:
        """
        解析股票列表Excel数据
        
        参数:
            content: Excel字节内容
            
        返回:
            pd.DataFrame - 包含标准化股票信息的DataFrame
        """
        logger.info("开始解析股票列表")
        
        try:
            # 使用openpyxl处理格式复杂的Excel文件更可靠
            df = pd.read_excel(
                BytesIO(content),
                engine='openpyxl',
                converters={'A股代码': self._clean_stock_code}  # 处理代码格式
            )
        except Exception as e:
            logger.error(f"Excel解析错误: {str(e)}")
            return pd.DataFrame()
            
        # 查找包含股票代码的列 (处理不同格式的表头)
        code_col = self._detect_column(df, 'A股代码')
        name_col = self._detect_column(df, 'A股简称')
        bk_col=self._detect_column(df, '板块')
        list_col=self._detect_column(df, 'A股上市日期')
        dq_col=self._detect_column(df, '地      区')
        sf_col=self._detect_column(df, '省    份')
        cs_col=self._detect_column(df, '城     市')
        hy_col=self._detect_column(df, '所属行业')

        if not code_col or not name_col:
            logger.error("未找到需要的列: 'A股代码' 和 'A股简称'")
            print("可用的列:", df.columns.tolist())
            return pd.DataFrame()
        
        # 选择并重命名所需列
        df = df.rename(columns={
            code_col: '股票代码',
            name_col: '股票简称',
            bk_col: '板块',
            list_col: '上市日期',
            dq_col: '地区',
            sf_col: '省份',
            cs_col: '城市',
            hy_col: '行业'
        }).loc[:, ['股票代码', '股票简称', '板块', '上市日期', '地区', '省份', '城市', '行业']]
        
        # 数据清理
        df = (
            df
            .dropna(subset=['股票代码'])
            #.query("`股票代码` != '-' and `股票代码` != '\\N'")
            .copy()
        )
        
        if df.empty:
            logger.warning("解析后没有获得有效数据")
            return pd.DataFrame()
            
        logger.info(f"成功解析 {len(df)} 条股票数据")
        return df.reset_index(drop=True)

    @staticmethod
    def _detect_column(df: pd.DataFrame, keyword: str) -> Optional[str]:
        """
        在DataFrame中查找包含关键字的列名
        
        返回匹配的列名，未找到则返回None
        """
        for col in df.columns:
            if keyword in str(col):
                return col
        return None

    @staticmethod
    def _clean_stock_code(code) -> str:
        """
        清理和标准化股票代码格式：
        - 去除空格
        - 补全为6位数字
        - 处理整数类型代码
        """
        if pd.isna(code) or code in ['-', '\\N']:
            return None
            
        # 转换为字符串处理
        code = str(code).strip()
        
        # 去除内部空格和特殊字符
        code = re.sub(r'[^\d]', '', code)
        
        # 补全前导零（深交所股票代码始终为6位）
        return code.zfill(6) if code and len(code) < 6 else code

    def fetch(self) -> Tuple[pd.DataFrame, int]:
        """
        完整下载和解析流程
        
        返回:
            (df, status_code)
            df: DataFrame包含股票信息
            status_code: 
                0 - 成功
                1 - 下载失败
                2 - 解析失败
        """
        content = self.download_stock_list()
        if content is None:
            return pd.DataFrame(), 1
            
        df = self.parse_stock_list(content)
        if df.empty:
            return pd.DataFrame(), 2
            
        return df, 0


def save_stock_list(df: pd.DataFrame, filename: str = "szse_stocks.csv"):
    """保存股票列表到CSV文件"""
    if df.empty:
        logger.error("无法保存空数据集")
        return False
        
    try:
        path = Path(filename)
        df.to_csv(path, index=False, encoding='utf-8-sig')
        logger.info(f"股票列表已保存到: {path.resolve()}")
        return True
    except Exception as e:
        logger.error(f"保存文件失败: {str(e)}")
        return False


def sz_fetch_stock_list():
    """主函数：执行整个流程"""
    logger.info("深交所股票列表获取...")
    
    fetcher = SZSEFetcher(timeout=15, max_retries=3)
    df, status = fetcher.fetch()
    
    if status == 0:
        # 显示结果
        print("\n获取的股票列表样本:")
        print(df.head())
        print(f"\n共获取 {len(df)} 只股票")
        
        # 保存结果
        # save_stock_list(df, "shenzhen_stocks.csv")
        
        # 验证数据分布
        if not df.empty:
            prefix_dist = df['股票代码'].str[:3].value_counts()
            print("\n股票代码前缀分布:")
            print(prefix_dist.head())
    elif status == 1:
        logger.error("程序因下载失败而终止")
    elif status == 2:
        logger.error("程序因解析失败而终止")
    
    logger.info("程序执行完毕")
    return df

if __name__ == "__main__":
    sz_fetch_stock_list()
