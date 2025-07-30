import pydevd
import sys
from typing import Dict, List, Any, Optional
import json
import os
from contextlib import contextmanager

class PydevdTracer:
    def __init__(self):
        self.trace_output = []
        self.current_frame = None
        self.variables = {}
        
    @contextmanager
    def trace_context(self):
        """设置和清理跟踪环境的上下文管理器"""
        try:
            # 设置跟踪器
            pydevd.settrace(
                suspend=False,  # 不暂停执行
                trace_only_current_thread=True,  # 只跟踪当前线程
                patch_multiprocessing=False,  # 不跟踪多进程
                stop_at_frame=None,
            )
            yield
        finally:
            # 清理跟踪器
            pydevd.stoptrace()

    def trace_execution(self, code: str, func_name: str, test_case: str) -> Dict[str, Any]:
        """
        跟踪代码执行并收集变量信息
        
        Args:
            code: 要执行的代码
            func_name: 要跟踪的函数名
            test_case: 测试用例
            
        Returns:
            包含执行跟踪信息的字典
        """
        self.trace_output = []
        
        # 准备完整的代码
        full_code = f"{code}\n\n{test_case}"
        
        # 设置跟踪回调
        def trace_callback(frame, event, arg):
            # 只跟踪目标函数
            if frame.f_code.co_name == func_name:
                self.handle_trace_event(frame, event, arg)
            return trace_callback
        
        # 执行带跟踪的代码
        with self.trace_context():
            sys.settrace(trace_callback)
            try:
                # 在临时命名空间中执行代码
                namespace = {}
                exec(full_code, namespace)
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "trace": self.trace_output
                }
            finally:
                sys.settrace(None)
        
        return {
            "status": "success",
            "trace": self.trace_output
        }

    def handle_trace_event(self, frame, event: str, arg: Any):
        """处理跟踪事件"""
        if event == 'call':
            # 函数调用开始
            self._handle_call(frame)
        elif event == 'line':
            # 每行代码执行
            self._handle_line(frame)
        elif event == 'return':
            # 函数返回
            self._handle_return(frame, arg)
        elif event == 'exception':
            # 异常发生
            self._handle_exception(frame, arg)

    def _handle_call(self, frame):
        """处理函数调用事件"""
        self.current_frame = frame
        # 收集函数参数
        args = self._get_function_arguments(frame)
        self.trace_output.append({
            'event': 'call',
            'line': frame.f_lineno,
            'arguments': args,
            'variables': self._get_variables(frame)
        })

    def _handle_line(self, frame):
        """处理行执行事件"""
        self.current_frame = frame
        self.trace_output.append({
            'event': 'line',
            'line': frame.f_lineno,
            'code': self._get_line_content(frame),
            'variables': self._get_variables(frame)
        })

    def _handle_return(self, frame, return_value):
        """处理函数返回事件"""
        self.trace_output.append({
            'event': 'return',
            'line': frame.f_lineno,
            'return_value': self._format_value(return_value),
            'variables': self._get_variables(frame)
        })
        self.current_frame = None

    def _handle_exception(self, frame, exc_info):
        """处理异常事件"""
        exc_type, exc_value, exc_traceback = exc_info
        self.trace_output.append({
            'event': 'exception',
            'line': frame.f_lineno,
            'exception_type': exc_type.__name__,
            'exception_message': str(exc_value),
            'variables': self._get_variables(frame)
        })

    def _get_variables(self, frame) -> Dict[str, Any]:
        """获取当前帧的所有变量"""
        variables = {}
        
        # 局部变量
        variables.update(frame.f_locals)
        
        # 过滤掉内部变量和函数
        return {
            k: self._format_value(v) 
            for k, v in variables.items() 
            if not k.startswith('__') and not callable(v)
        }

    def _get_function_arguments(self, frame) -> Dict[str, Any]:
        """获取函数参数"""
        args = {}
        code = frame.f_code
        # 获取参数名
        arg_names = code.co_varnames[:code.co_argcount]
        for arg_name in arg_names:
            if arg_name in frame.f_locals:
                args[arg_name] = self._format_value(frame.f_locals[arg_name])
        return args

    def _get_line_content(self, frame) -> str:
        """获取当前行的代码内容"""
        try:
            with open(frame.f_code.co_filename, 'r') as f:
                lines = f.readlines()
                return lines[frame.f_lineno - 1].strip()
        except:
            return "<source not available>"

    def _format_value(self, value: Any) -> str:
        """格式化变量值为字符串"""
        try:
            # 对于简单类型直接返回字符串表示
            if isinstance(value, (int, float, str, bool, type(None))):
                return repr(value)
            # 对于集合类型，限制长度
            if isinstance(value, (list, tuple, set, dict)):
                return str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
            # 对于其他类型，返回类型名称
            return f"<{type(value).__name__}>"
        except:
            return "<unprintable>"

    def format_trace_output(self) -> str:
        """格式化跟踪输出为易读的字符串"""
        output = []
        for entry in self.trace_output:
            if entry['event'] == 'call':
                output.append(f"Function call at line {entry['line']}")
                output.append(f"Arguments: {entry['arguments']}")
            elif entry['event'] == 'line':
                output.append(f"Line {entry['line']}: {entry['code']}")
                output.append(f"Variables: {entry['variables']}")
            elif entry['event'] == 'return':
                output.append(f"Return at line {entry['line']}")
                output.append(f"Return value: {entry['return_value']}")
            elif entry['event'] == 'exception':
                output.append(f"Exception at line {entry['line']}")
                output.append(f"{entry['exception_type']}: {entry['exception_message']}")
            output.append("-" * 50)
        return "\n".join(output) 