module {{ module_name }}_wrapper
   import sense_pkg::*;
(
{%- for p in port_obj_lst %}
    {%- if loop.last %}
    {{ p.direction }}  logic {{ p.width if p.width is not none else "" }} {{ p.name }}
    {%- else %}
    {{ p.direction }}  logic {{ p.width if p.width is not none else "" }} {{ p.name }},
    {%- endif %}
{%- endfor %}
);


{{ module_instance }}

endmodule
