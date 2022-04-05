# alpha updaters

## Concepto

Los $\alpha$ updaters son una forma rapida de crear animaciones personalizadas.
Se usan cuando necesitas que realizar una animación muy específica unas pocas veces. En caso de que necesites aplicar esa animación muchas veces, lo mejor es crear una animación personalizada, esto lo veremos en el próximo capítulo.

El parámetro alpha representa básicamente el progreso del run_time de una rate_function.

Si tienes una animación de este estilo:

```python
Scene.play(Animation(mob,run_time=5,rate_func=smooth))
```

Entonces alpha al 20% es 1 segundo, alpha al 50% es 2.5 segundos, y alpha al 100% es 5 segundos.

/Inserta imagen

Eso es lo que significa el parámetro alpha en las animaciones.

Para definir un alpha updater se tiene que obedecer el siguiente formato:

```python
def my_alpha_updater(mob, alpha): # mob, vmob, grp, vgr. etc
    color = interpolate_color(RED,BLUE,alpha)
    mob.set_color(color)
```

Los alpha updaters son funciones que reciben como parámetros un solo Mobject, seguido del parámetro alpha. Es obligatorio que el segundo parámetro se llame alpha, para que Manim lo interprete de forma correcta.

En el código anterior estamos animando el cambio de color de RED a BLUE.

Al inicio, alpha=0, por lo que mob va a ser color RED, si estamos usando una rate_func como linear o smooth, cuando alpha=50% entonces el color será morado.

Y cuando la animación termine (si estamos usando una rate_func como linear o smooth) entonces el color será azul.

La manera de usar un alpha updater es de la siguiente forma:

```python
square = Square()

Scene.play(
    UpdateFromAlphaFunc(square, my_alpha_updater,run_time=4,rate_func=smooth)
)
```

La animación UpdateFromAlphaFunc recibe como primer argumento el Mobject al que se le va aplicar el updater, y como segundo argumento el updater. Y como cualquier animación recibe run_time, rate_func y remover.

El código completo es así:

```python
class Example(Scene):
    def construct(self):
        square = Square()

        def my_alpha_updater(mob, alpha):
            color = interpolate_color(RED,BLUE,alpha)
            mob.set_color(color)

        self.play(
            UpdateFromAlphaFunc(square, my_alpha_updater,run_time=4,rate_func=smooth)
        )
        self.wait()
%manim $_RV
```

## Pro-tip: Closure

Si usamos el concepto de Closure (como lo vimos en el curso anterior) entonces podríamos hacer algo como esto:

```python
class Example(Scene):
    def construct(self):
        square = Square()

        def anim_interpolate_color(c1,c2):
            def updater(mob, alpha):
                color = interpolate_color(c1,c2,alpha)
                mob.set_color(color)
            return updater

        self.play(
            UpdateFromAlphaFunc(
                square, anim_interpolate_color(YELLOW,TEAL),
                run_time=4,rate_func=smooth
            )
        )
        self.wait()
%manim $_RV
```

Una forma muy rápida (algo limitada, y poco elegante) de crear animaciones personalizadas es de esta forma:

```python
def anim_interpolate_color(c1,c2):
    def updater(mob, alpha):
        color = interpolate_color(c1,c2,alpha)
        mob.set_color(color)
    return updater

def InterpolateColor(mob,c1,c2,**kwargs):
    return UpdateFromAlphaFunc(
                mob, anim_interpolate_color(c1,c2),
                **kwargs
            )

class Example(Scene):
    def construct(self):
        square = Square()
        self.play(
            Interpolatecolor(square,PURPLE,ORANGE,rate_func=there_and_back)
        )
        self.wait()
%manim $_RV
```

En el próximo capítulo veremos la mejor manera de crear animaciones personalizadas.

## Pro-tip 2: Usar save_state e interpolate.


En el curso anterior vimos que no es una buena idea usar la animación Transform para animar rotaciones, pero los alpha updaters son ideales para hacer rotaciones.

Te puedes ver tentado a hacerlo de la siguiente forma:

```python
class Example(Scene):
    def construct(self):
        square = Square()

        def updater(mob, alpha):
            angle = 40 * DEGREES * alpha
            mob.rotate(angle)

        self.play(
            UpdateFromAlphaFunc(
                square, updater,
                run_time=1,rate_func=smooth
            )
        )
        self.wait()
%manim $_RV
```


Pero vemos que esto no funciona, esto se debe a que cada frame de la animación estamos rotando 40 * DEGREES * alpha, es decir, si renderizamos esto a 60fps:

* Frame 1 (alpha=0/60): angle = 40 * DEGREES * 0/60 = 0.0 * DEGREES
* Frame 2 (alpha=1/60): angle = 40 * DEGREES * 1/60 = 0.66 * DEGREES
* Frame 3 (alpha=2/60): angle = 40 * DEGREES * 2/60 = 1.33 * DEGREES
* Frame 4 (alpha=3/60): angle = 40 * DEGREES * 3/60 = 2.0 * DEGREES
* Frame 5 (alpha=4/60): angle = 40 * DEGREES * 4/60 = 2.66 * DEGREES
* Frame 6 (alpha=5/60): angle = 40 * DEGREES * 5/60 = 3.33 * DEGREES

Esto es, cada frame que pasa el ángulo de rotación incrementa, lo cual no es lo deseado.

Para resolver esto hay que "recordar" el estado inicial del Mobject, para que, cada inicio de frame, se restaure al estado inicial, y luego le apliquemos el ángulo.

```python
class Example(Scene):
    def construct(self):
        square = Square()
        square.save_state()

        def updater(mob, alpha):
            mob.restore()
            mob.rotate(40 * DEGREES * alpha)

        self.play(
            UpdateFromAlphaFunc(
                square, updater,
                run_time=1,rate_func=smooth
            )
        )
        self.wait()
%manim $_RV
```

Una función que suele ser bastante utilizada junto con los alpha updaters es interpolate, que como su nombre indica, interpola un valor entre dos extremos, usando in parámetro alpha (similar a interpolate_color). Lo entenderemos mejor con el siguiente ejemplo.

```python
class Example(Scene):
    def construct(self):
        square = Square()
        initial_width = square.width
        end_width     = 6

        def updater(mob, alpha):
            new_width = interpolate(initial_width,end_width,alpha)
            mob.set(width=new_width)

        self.play(
            UpdateFromAlphaFunc(
                square, updater,
                run_time=1,rate_func=smooth
            )
        )
        self.wait()
%manim $_RV
```