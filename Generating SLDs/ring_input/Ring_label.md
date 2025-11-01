ROW AUTHORITIES
'<b><font color="red">' || "road_autho" || '</font> <br>
</b> <font color="blue">' ||  replace("span_name", 'TO', '<br>TO') || '</font>'

size=3.5

repeating at 2500
overrun distance 1000


#OUTPUT POINTS
'<font color="Blue"><b>' ||
coalesce("Point Name", '') ||'<br>'||
'</font>' ||
'<font color="#830001">' ||
round(y($geometry), 6) || ', ' || round(x($geometry), 6) ||
'</font>'


size=4

