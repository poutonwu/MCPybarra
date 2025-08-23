import sys
import os
from typing import Optional, Tuple
from PIL import Image, UnidentifiedImageError
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("image_converter")

# 支持的图像格式映射表（保持与PIL库兼容）
SUPPORTED_FORMATS = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "bmp": "BMP",
    "gif": "GIF"
}

def _validate_image_path(image_path: str) -> None:
    """验证图像文件路径是否存在且可读"""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"输入图像文件不存在: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            f.read(16)  # 尝试读取文件头部，验证是否可读
    except IOError as e:
        raise PermissionError(f"无法读取图像文件: {e}")

def _validate_output_dir(output_dir: str) -> None:
    """验证输出目录是否存在，若不存在则尝试创建"""
    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            raise PermissionError(f"无法创建输出目录: {e}")

def _determine_format(filename: str, format: Optional[str]) -> str:
    """确定目标图像格式：优先使用用户指定格式，否则从文件扩展名推断"""
    if format is not None:
        format = format.lower()
        if format in SUPPORTED_FORMATS:
            return SUPPORTED_FORMATS[format]
        else:
            supported_list = ', '.join(SUPPORTED_FORMATS.keys())
            raise ValueError(f"不支持的目标格式: {format}。支持的格式有: {supported_list}")
    
    ext = os.path.splitext(filename)[1][1:].lower()
    if ext in SUPPORTED_FORMATS:
        return SUPPORTED_FORMATS[ext]
    
    supported_list = ', '.join(SUPPORTED_FORMATS.keys())
    raise ValueError(f"无法识别目标格式: 文件扩展名为.{ext}。支持的格式有: {supported_list}")

def _convert_image_mode(img: Image.Image, target_format: str) -> Image.Image:
    """根据目标格式自动处理颜色空间转换"""
    if target_format == "JPEG":
        if img.mode in ("RGBA", "LA"):
            # JPEG不支持透明通道，转为RGB
            return img.convert("RGB")
        elif img.mode != "RGB":
            return img.convert("RGB")
    elif target_format == "GIF":
        if img.mode == "RGBA":
            # GIF支持透明度但需要调色板，先处理透明像素再转换
            alpha = img.split()[3]
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img.convert("RGB"), mask=alpha)
            return bg
        elif img.mode != "P":
            return img.convert("P", palette=Image.ADAPTIVE)
    
    return img  # 默认保持原样

def _generate_output_path(input_path: str, output_dir: str, 
                         target_format: str) -> Tuple[str, str]:
    """生成输出文件路径和文件名"""
    filename = os.path.basename(input_path)
    name, _ = os.path.splitext(filename)
    
    ext_map = {v: k for k, v in SUPPORTED_FORMATS.items()}
    target_ext = ext_map.get(target_format, target_format.lower())
    
    output_filename = f"{name}_converted.{target_ext}"
    output_path = os.path.join(output_dir, output_filename)
    
    return output_path, output_filename

@mcp.tool()
def convert_image(input_path: str, output_dir: str, format: Optional[str] = None) -> dict:
    """
    将各种图像文件格式（如PNG、JPEG、BMP、GIF等）相互转换，支持处理包含透明度的RGBA图像，
    自动执行适当的颜色空间转换，并将转换后的图像保存至指定目录。
    
    Args:
        input_path: 输入图像文件的完整路径 (必填)。
        output_dir: 转换后图像文件的输出目录 (必填)。
        format: 目标格式名称 (可选，默认从输出文件扩展名推断)。
                支持的格式: png, jpg, jpeg, bmp, gif
    
    Returns:
        一个包含转换结果信息的字典，结构如下：
        {
            "status": "success" or "error",
            "output_path": "转换后的文件路径 (成功时存在)",
            "message": "详细的操作信息或错误描述"
        }
    
    Raises:
        FileNotFoundError: 如果输入图像文件不存在。
        PermissionError: 如果输入文件不可读或输出目录不可写。
        ValueError: 如果输入参数无效或目标格式不受支持。
        RuntimeError: 如果图像转换过程中发生严重错误。
    """
    result = {"status": "success"}
    
    try:
        # --- 健壮性: 输入验证 ---
        _validate_image_path(input_path)
        _validate_output_dir(output_dir)
        
        # --- 功能性: 核心图像转换逻辑 ---
        with Image.open(input_path) as img:
            target_format = _determine_format(input_path, format)
            converted_img = _convert_image_mode(img, target_format)
            
            output_path, output_filename = _generate_output_path(
                input_path, output_dir, target_format
            )
            
            converted_img.save(output_path, format=target_format)
            
            result.update({
                "output_path": output_path,
                "message": f"成功将 {input_path} 转换为 {target_format} 格式 ({output_filename})"
            })
    
    except FileNotFoundError as e:
        result.update({"status": "error", "message": str(e)})
        raise
    except PermissionError as e:
        result.update({"status": "error", "message": str(e)})
        raise
    except ValueError as e:
        result.update({"status": "error", "message": str(e)})
        raise
    except UnidentifiedImageError as e:
        error_msg = f"PIL无法识别图像文件: {e}"
        result.update({"status": "error", "message": error_msg})
        raise ValueError(error_msg) from e
    except Exception as e:
        error_msg = f"图像转换过程中发生未知错误: {e}"
        result.update({"status": "error", "message": error_msg})
        raise RuntimeError(error_msg) from e
    
    return result

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()