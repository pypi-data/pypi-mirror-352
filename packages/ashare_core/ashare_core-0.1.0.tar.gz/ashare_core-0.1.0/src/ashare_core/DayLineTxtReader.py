import pandas as pd
import re
from pathlib import Path
from typing import List, Union
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def read_single_stock_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """读取单个股票数据文件并转换为DataFrame"""
    try:
        # 转换为Path对象
        path = Path(file_path)
        # 读取所有行
        lines = path.read_text(encoding='gbk').splitlines()
        
        # 创建结果列表
        result = []
        
        # 解析第一行 - 使用正则分割处理连续空格
        if not lines:
            return pd.DataFrame()
        
        first_line = lines[0].strip()
        header_parts = re.split(r'\s+', first_line)
        if len(header_parts) < 4:
            raise ValueError(f"文件格式错误，第一行缺少必要字段: {first_line}")
        
        stock_code = header_parts[0]
        stock_name = header_parts[1]
        data_type = header_parts[2]
        adjustment_type = header_parts[3]
        
        # 解析数据行（跳过标题行和注释行）
        data = []
        for line in lines[1:]:
            stripped_line = line.strip()
            # 跳过标题行、注释行和空行
            if not stripped_line or stripped_line.startswith('#') or '日期' in stripped_line:
                continue
            
            # 分隔数据并清理空格
            row_data = [field.strip() for field in stripped_line.split(',')]
            if len(row_data) == 7:  # 有7个字段
                data.append(row_data)
        
        if not data:
            raise ValueError("文件中未找到有效数据")
        
        # 创建DataFrame
        df = pd.DataFrame(
            data, 
            columns=['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']
        )
        
        # 添加股票元数据
        df.insert(0, '股票代码', stock_code)
        df.insert(1, '股票名称', stock_name)
        df.insert(2, '数据类型', data_type)
        df.insert(3, '除权类型', adjustment_type)
        df.insert(4, '来源文件', path.name)  # 添加文件名以便追踪
        
        return df
        
    except Exception as e:
        raise RuntimeError(f"读取文件失败 {file_path}: {e}")


def read_multiple_stock_data(folder_path: Union[str, Path]) -> pd.DataFrame:
    """
    读取文件夹下所有txt文件并合并为单个DataFrame
    
    参数:
    folder_path: 包含股票数据文件的文件夹路径
    
    返回:
    包含所有股票数据的合并DataFrame
    """
    # 转换为Path对象
    path = Path(folder_path)
    
    # 验证文件夹存在
    if not path.exists():
        raise FileNotFoundError(f"指定文件夹不存在: {folder_path}")
    if not path.is_dir():
        raise NotADirectoryError(f"指定路径不是文件夹: {folder_path}")
    
    # 收集所有txt文件
    all_files = list(path.glob('*.txt'))
    print(f"在文件夹 {folder_path} 中找到 {len(all_files)} 个txt文件")
    
    # 并行读取所有文件
    dfs = []
    skipped_files = []
    
    for file in all_files:
        try:
            print(f"处理文件: {file.name}")
            df = read_single_stock_data(file)
            dfs.append(df)
        except Exception as e:
            print(f"  × 跳过文件 {file.name}: {str(e)}")
            skipped_files.append(file.name)
    
    # 合并所有DataFrame
    if not dfs:
        print("警告: 没有成功读取任何文件")
        return pd.DataFrame()
    
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # 报告结果
    print(f"成功读取 {len(dfs)} 个文件, 跳过 {len(skipped_files)} 个文件")
    if skipped_files:
        print("跳过的文件列表:")
        for file in skipped_files:
            print(f"  - {file}")
    
    return merged_df
columns = {
    "股票代码": "code",
    "股票名称": "name",
    "数据类型": "DataType",
    "除权类型": "ExRightType",
    "来源文件": "SourceFile",
    "日期": "date",
    "开盘": "open",
    "最高": "high",
    "最低": "low",
    "收盘": "close",
    "成交量": "volume",
    "成交额": "value"
}

class DayLineTxtReader:
    """股票数据读取器"""
    
    def __init__(self, data_path: Union[str, Path]):
        self.data_path = Path(data_path)
        if not self.data_path.is_dir():
            raise FileNotFoundError(f"数据目录不存在或不是文件夹: {self.data_path}")
        logging.info(f"数据读取器已初始化，数据目录: {self.data_path}")

    def read(self,code: str) -> pd.DataFrame:
        """
        读取指定股票代码的数据
        
        参数:
        code: 股票代码
        
        返回:
        包含指定股票数据的DataFrame
        """
        file_path = self.data_path / f"{code}.txt"
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        df= read_single_stock_data(file_path)
        df['日期'] = pd.to_datetime(df['日期'], format='%Y/%m/%d')
        numeric_cols = ['开盘', '最高', '最低', '收盘', '成交量', '成交额']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        df.rename(columns=columns, inplace=True)
        logging.info(f"成功读取股票 {code} 的,{len(df)}条数据") 
        return df
    def read_multiple(self,codes: List[str]) -> pd.DataFrame:
        """
        读取多个股票代码的数据
        
        参数:
        codes: 股票代码列表
        
        返回:
        包含所有指定股票数据的合并DataFrame
        """
        dfs = []
        for code in codes:
            try:
                df = self.read(code)
                dfs.append(df)
            except Exception as e:
                # 抛出异常
                raise RuntimeError(f"读取股票 {code} 时出错: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
if __name__ == "__main__":
    folder_path = r"C:\data\导出"  # 修改为你的文件夹路径
    Reader = DayLineTxtReader(folder_path)
    
    try:
        big_df = Reader.read_multiple(['SZ#000012', 'SH#600651', 'SZ#000538'])  # 示例股票代码
        if not big_df.empty:
            # 优化数据类型以节省内存
            print("\n合并后的DataFrame信息:")
            print(big_df.info())
            print("\n前几行示例:")
            print(big_df.head())
           
        else:
            print("没有数据可以保存")
            
    except Exception as e:
        print(f"处理过程中出错: {e}")
