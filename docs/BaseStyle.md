BaseStyle Class
=

The purpose of the BaseStyle class is to make managing style properties a lot
easier. It allows one to build complex style profiles and manage properties for 
any object. Unlike the other Base Classes in PyMapKit, BaseStyle can be used 
directly without being subclassed (though it can be).

When initializing a BaseStyle object, it requires a "styled object". An object 
that the new BaseStyle object is responsible for managing the style for. The 
BaseStyle and will dynamically add and remove styling methods to the styled 
object.

After initializing a BaseStyle object, it needs to be setup. This means building
a style profile using the add_domain, add_mode, add_property, and set_mode 
methods. These correspond to the profiles items: domain, mode, and property.

A property is a named value, such as background_color, or line_weight. A 
property can be added to a mode, or a domain, or be top level, not belonging to 
any mode or domain. 

A mode is a set of properties that are turned on or off when that mode is 
active. A mode normally belongs to a domain

A domain is a set of properties and modes, that manage a specific aspect of the
styled object. They are used to help separate properties

 For example, a polygon object has two domains: a background 
domain, and an outline domain. These domains need separate 