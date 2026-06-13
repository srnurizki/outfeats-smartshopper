"use client"

import { useEffect, useRef } from "react"

const VERT = `attribute vec2 p;void main(){gl_Position=vec4(p,0,1);}`

const FRAG = `precision highp float;uniform vec2 r;uniform vec2 m;uniform float t;
vec3 pal(float x){vec3 a=vec3(.55,.55,.65);vec3 b=vec3(.25,.2,.25);vec3 c=vec3(1.,.8,1.);vec3 d=vec3(.1,.25,.5);return a+b*cos(6.28318*(c*x+d));}
float sn(vec2 p){vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.-2.*f);
float a=fract(sin(dot(i,vec2(127.1,311.7)))*43758.5453);
float b=fract(sin(dot(i+vec2(1,0),vec2(127.1,311.7)))*43758.5453);
float c=fract(sin(dot(i+vec2(0,1),vec2(127.1,311.7)))*43758.5453);
float d=fract(sin(dot(i+vec2(1,1),vec2(127.1,311.7)))*43758.5453);
return mix(mix(a,b,f.x),mix(c,d,f.x),f.y);}
void main(){vec2 uv=gl_FragCoord.xy/r;vec2 ms=m/r;float ti=t*.3;
float md=length(uv-ms);float inf=exp(-md*2.5);
float n1=sn(uv*3.+ti*.4+ms*1.5);float n2=sn(uv*5.-ti*.3+ms*2.);float n3=sn(uv*2.+ti*.2+inf*.8);
float w1=sin(uv.x*4.+ti+ms.x*3.)*.5+.5;float w2=sin(uv.y*3.-ti*1.2+ms.y*2.5)*.5+.5;
float w3=sin((uv.x+uv.y)*2.5+ti*.8)*.5+.5;
float f=fract(n1*.3+n2*.2+n3*.15+w1*.15+w2*.12+w3*.08+inf*.15);
vec3 col=pal(f);float sh=pow(max(0.,1.-md*1.8),3.)*.3;col+=sh*vec3(.9,.95,1.);
col=pow(mix(col,col*1.08,smoothstep(.3,.7,n1)),vec3(.9));
gl_FragColor=vec4(col,1.);}`

export default function LiquidChrome() {
    const canvasRef = useRef<HTMLCanvasElement>(null)

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return
        const gl = canvas.getContext("webgl")
        if (!gl) return

        const compile = (type: number, src: string) => {
            const s = gl.createShader(type)!
            gl.shaderSource(s, src)
            gl.compileShader(s)
            return s
        }

        const prog = gl.createProgram()!
        gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT))
        gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG))
        gl.linkProgram(prog)
        gl.useProgram(prog)

        const buf = gl.createBuffer()
        gl.bindBuffer(gl.ARRAY_BUFFER, buf)
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW)

        const pa = gl.getAttribLocation(prog, "p")
        gl.enableVertexAttribArray(pa)
        gl.vertexAttribPointer(pa, 2, gl.FLOAT, false, 0, 0)

        const ur = gl.getUniformLocation(prog, "r")
        const um = gl.getUniformLocation(prog, "m")
        const ut = gl.getUniformLocation(prog, "t")

        let W = 0, H = 0, mx = 0, my = 0, tx = 0, ty = 0, t0: number | null = null
        let rafId = 0

        const resize = () => {
            W = canvas.width = window.innerWidth
            H = canvas.height = window.innerHeight
            gl.viewport(0, 0, W, H)
            mx = tx = W / 2
            my = ty = H / 2
        }

        const onMove = (e: MouseEvent) => {
            tx = e.clientX
            ty = H - e.clientY
        }

        const frame = (ts: number) => {
            if (t0 === null) t0 = ts
            mx += (tx - mx) * 0.05
            my += (ty - my) * 0.05
            gl.uniform2f(ur, W, H)
            gl.uniform2f(um, mx, my)
            gl.uniform1f(ut, (ts - t0) / 1000)
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
            rafId = requestAnimationFrame(frame)
        }

        resize()
        window.addEventListener("resize", resize)
        window.addEventListener("mousemove", onMove)
        rafId = requestAnimationFrame(frame)

        return () => {
            window.removeEventListener("resize", resize)
            window.removeEventListener("mousemove", onMove)
            cancelAnimationFrame(rafId)
        }
    }, [])

    return (
    <canvas
        ref={canvasRef}
        style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            zIndex: -1,
            pointerEvents: 'none'
        }}
    />
)
}