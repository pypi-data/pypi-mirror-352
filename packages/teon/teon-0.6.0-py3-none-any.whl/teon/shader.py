VERTEX_SHADER = '''
#version 330
in vec2 in_pos;
in vec2 in_uv;
out vec2 uv;

uniform vec2 camera_offset;
uniform float zoom;

void main() {
    uv = in_uv;
    vec2 pos = (in_pos - camera_offset) * zoom;
    gl_Position = vec4(pos, 0.0, 1.0);
}
'''

FRAGMENT_SHADER = '''
#version 330
in  vec2 uv;
out vec4 frag_color;

uniform sampler2D tex;
uniform float u_alpha;   // 0.0 = fully transparent, 1.0 = original image alpha

void main() {
    vec4 texel = texture(tex, uv);
    texel.a *= u_alpha;      // scale the alpha channel
    frag_color = texel;
}
'''
