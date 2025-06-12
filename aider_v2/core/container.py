"""Dependency injection container for managing service dependencies."""

from typing import Dict, Type, Any, TypeVar, Callable, Optional
import inspect

T = TypeVar('T')


class Container:
    """Simple dependency injection container."""
    
    def __init__(self) -> None:
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
    
    def register(self, interface: Type[T], implementation: Type[T], singleton: bool = False) -> None:
        """Register a service implementation."""
        self._services[interface] = (implementation, singleton)
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T], singleton: bool = False) -> None:
        """Register a factory function for creating service instances."""
        self._factories[interface] = (factory, singleton)
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a specific instance as a singleton."""
        self._singletons[interface] = instance
    
    def get(self, interface: Type[T]) -> T:
        """Get a service instance."""
        # Check if we have a singleton instance
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check if we have a factory
        if interface in self._factories:
            factory, is_singleton = self._factories[interface]
            instance = factory()
            
            if is_singleton:
                self._singletons[interface] = instance
            
            return instance
        
        # Check if we have a registered service
        if interface not in self._services:
            raise ValueError(f"Service {interface.__name__} not registered")
        
        implementation, is_singleton = self._services[interface]
        instance = self._create_instance(implementation)
        
        if is_singleton:
            self._singletons[interface] = instance
        
        return instance
    
    def _create_instance(self, implementation: Type[T]) -> T:
        """Create an instance with dependency injection."""
        # Get constructor signature
        sig = inspect.signature(implementation.__init__)
        
        # Build constructor arguments
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Try to resolve the parameter type
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.get(param.annotation)
                except ValueError:
                    # If we can't resolve it and there's no default, raise an error
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(f"Cannot resolve dependency {param.annotation} for {implementation}")
        
        return implementation(**kwargs)
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()


# Global container instance
container = Container()