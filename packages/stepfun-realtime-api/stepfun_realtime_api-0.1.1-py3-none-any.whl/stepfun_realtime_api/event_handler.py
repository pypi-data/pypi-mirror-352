import asyncio
from typing import Dict, List, Callable, Any, Optional
import traceback

class RealtimeEventHandler:
    def __init__(self):
        self.one_time_map: Dict[str, List[Callable]] = {}
        self.handler_map: Dict[str, List[Callable]] = {}
    
    def clear(self):
        self.one_time_map.clear()
        self.handler_map.clear()
    
    def on(self, event_type: str, handler: Callable):
        if event_type not in self.handler_map:
            self.handler_map[event_type] = []
        self.handler_map[event_type].append(handler)
    
    def off(self, event_type: str, handler: Callable):
        if event_type not in self.handler_map:
            return
        handlers = self.handler_map[event_type]
        if handler in handlers:
            handlers.remove(handler)
    
    def once(self, event_type: str, handler: Callable):
        if event_type not in self.one_time_map:
            self.one_time_map[event_type] = []
        self.one_time_map[event_type].append(handler)
    
    def off_once(self, event_type: str, handler: Callable):
        if event_type not in self.one_time_map:
            return
        handlers = self.one_time_map[event_type]
        if handler in handlers:
            handlers.remove(handler)
    
    async def wait_for_next(self, event_type: str, timeout_ms: int = 0) -> Optional[Any]:
        future = asyncio.get_event_loop().create_future()
        
        def handler(event: Any):
            if not future.done():
                future.set_result(event)
        
        self.once(event_type, handler)
        
        if timeout_ms > 0:
            try:
                return await asyncio.wait_for(future, timeout_ms / 1000)
            except asyncio.TimeoutError:
                return None
        else:
            return await future
    
    def dispatch(self, event_type: str, event: Any):
        # 调用常规处理程序
        for handler in self.handler_map.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                last_frame = tb[-1]  # Get the last frame (where the error occurred)
                print(f"Error in handler for event type {event_type}: {e}")
                print(f"Error occurred at {last_frame.filename}:{last_frame.lineno} - {last_frame.line}")
        
        # 调用一次性处理程序
        one_time_handlers = self.one_time_map.get(event_type, [])
        for handler in one_time_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in one-time handler for event type {event_type}: {e}")
        
        # 清除一次性处理程序
        if event_type in self.one_time_map:
            del self.one_time_map[event_type]