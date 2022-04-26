# CH2 - Animaciones personalizadas

## Estructura de una animación.

Esta clase es una simplificación y extensión de este [tutorial](https://www.youtube.com/watch?v=xqENEC1URKk) de **Benjamin Hackl** (un miembro del equipo de desarrollo de ManimCE).

Vamos a estudiar el ejemplo de la animación Rotating para entender el esqueleto de una animación:

```python
class Rotating(Animation):
    def __init__(
        self,
        mobject: Mobject,
        axis: np.ndarray = OUT,
        radians: np.ndarray = TAU,
        about_point: np.ndarray | None = None,
        about_edge: np.ndarray | None = None,
        run_time: float = 5,
        rate_func: Callable[[float], float] = linear,
        **kwargs,
    ) -> None:
        self.axis = axis
        self.radians = radians
        self.about_point = about_point
        self.about_edge = about_edge
        super().__init__(mobject, run_time=run_time, rate_func=rate_func, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject.become(self.starting_mobject)
        self.mobject.rotate(
            self.rate_func(alpha) * self.radians,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )
```

### Puntos a resaltar:

1. Para crear una animación debes crear una clase que herede de `Animation` o de una subclase de `Animation`.
2. Toda animación está atada a un Mobject, este mobject será asignado como atributo a la animación `self.mobject`.
3. Toda animación tiene `run_time` (duración), `rate_func` (comportamiento), `remover`, etc. Si no las definimos entonces se van a usar los valores por defecto de `Animation`.
4. Resalmemos que existe un atributo llamado `starting_mobject` que no hemos definido.
5. Estamos redefiniendo (overwrite) el método `interpolate_mobject`.
6. Estamos usando el método `rate_func`.

### Explicación:

Analicemos el siguiente código:

```python
class Example(Scene):
    def construct(self):
        sq = Square().scale(2)
        self.play(Rotating(sq,radians=PI/2,run_time=2))
        self.wait()

%manim $_RV
```

Cuando el intérprete de Python llega el método `play`, en ese momento va a ejecutar una serie de procedimientos a cada animación que esté dentro de el.

El procedimiento es el siguiente:

1. Se crea un atributo llamado `mobject`, este es el mobject que va a ser manipulado, y que por lo tanto va a cambiar, a lo largo de la animación.
2. También se crea un atributo llamado `starting_mobject`, el cual es una copia del `mobject` al inicio de la animación.
3. Se va a ejecutar el método `begin` que tienen todas las clases que heredan de `Animation`:

    * En caso de que este mobject tenga un updater activo, este se va a suspender.
    * Por último, `begin` llama al método `interpolate` con el valor 0. Este método recibe un valor alpha (que va de 0 a 1), y su comportamiento depende de otros métodos que se explicarán a continuación.
    * El método `begin` solo se ejecuta una vez, al inicio de la animación.
4. La manera en cómo se va a indicar el progreso de la animación se puede definir de dos formas, con `interpolate_mobject` y con `interpolate_submobject`.
    * `interpolate_mobject` recibe el parámetro `alpha` y aquí se indica cómo va a ser cada paso de la animación. Se puede hacer uso de `Animation.mobject` o de `Animation.starting_mobject`, o de cualquier otro valor que hayas definido en `begin` o antes.
    * `interpolate_submobject` sirve para tener un mayor control de cada submobject del objeto (en caso de que sea un `VGroup` o similar), este método recibe tres parámetros, el submob que va a modificarse, el starting_submob, que es una copia del submob al inicio de la animación, y alpha.
    * <u style="color:red"><b>REMARK:</u></b> Es recomendable definir la linea `alpha = self.rate_func(alpha)` al inicio de estos métodos para que la animación respete la `rate_func` que definamos en el método `Scene.play`.
5. Se llama el método `finish` que renderiza el último frame.
6. Se llama al método `clean_up_from_scene`, que sirve principalmente para remover objetos que se hayan creado a lo largo de la animación, este es el método que elimina el objeto en caso de que `remover` sea `True`.

## Ejemplos con interpolate_mobject.

### Rotate and change color.

```python
class RotateAndColor(Animation):
    def __init__(
        self,
        mobject,
        angle = TAU,
        target_color = RED,
        run_time = 3,
        rate_func = linear,
        **kwargs,
    ):
        # set attrs
        self._angle = angle
        self._init_color = mobject.get_color()
        self._target_color = target_color
        super().__init__(mobject, run_time=run_time, rate_func=rate_func, **kwargs)

    def interpolate_mobject(self, alpha):
        # don't forget this line
        alpha = self.rate_func(alpha)
        # similar to mob.restore() (see previus chapter)
        self.mobject.become(self.starting_mobject)
        # rotate
        self.mobject.rotate(alpha * self._angle)
        # set color
        self.mobject.set_color(interpolate_color(
            self._init_color, self._target_color, alpha
        ))
```

```python
class Example(Scene):
    def construct(self):
        sq = Square().scale(2)
        self.play(RotateAndColor(sq, TAU, ORANGE))
        self.wait()

%manim $_RV
```

### Highlight animation.

Vamos a crear la siguiente animación:

![video](_static/_chp2_v1.mp4)

Vamos a realizar la animación, primero sin desvanecer el objeto.

```python
class Remark(Animation):
    # definimos los parámetros de entrada
    def __init__(self, mob, scale=1.3, color=RED, **kwargs):
        # definimos atributos iniciales
        self._scale = scale
        self._color = color
        super().__init__(mob, **kwargs)

    def begin(self):
        # creamos el objeto que se va a agrandar
        self.remark_mob = self.mobject.copy()
        self.remark_mob.set_color(self._color)
        # guardamos su estado inicial
        self.remark_mob.save_state()
        # lo añadimos al mobject, ESTO ES IMPORTANTE
        # si no hacemos esto no aparecerá en la animación
        self.mobject.add(self.remark_mob)
        super().begin()

    def interpolate_mobject(self, alpha):
        alpha = self.rate_func(alpha)
        # regresamos a su estado inicial
        self.remark_mob.restore()
        # No podemos hacer:
        # self.remark_mob.scale(self._scale * alpha)
        # porque alpha va de 0 a 1, por lo que no daría el
        # efecto deseado, por lo que lo mejor es:
        self.remark_mob.scale(interpolate(1,self._scale,alpha))

class Example(Scene):
    def construct(self):
        sq = Square().scale(2)
        self.play(Remark(sq, 1.7))
        self.play(sq.animate.shift(LEFT))
        self.wait()

%manim $_RV
```

Vemos que la animación no es la esperada, por un lado, porque no hemos removido el objeto `remark_mob` de la escena, esto lo podemos arreglar si añadimos el método `clean_up_from_scene`.

```python
class Remark(Remark):
    def clean_up_from_scene(self, scene):
        # remove extra mobs from self.mobject
        self.mobject.remove(self.remark_mob)
        # remove it also from screen
        scene.remove(self.remark_mob)
        # call super
        super().clean_up_from_scene(scene)

class Example(Scene):
    def construct(self):
        sq = Square().scale(2)
        self.play(Remark(sq, 1.7))
        self.play(sq.animate.shift(LEFT))
        self.wait()

%manim $_RV
```

Y para finalizar, añadimos el fade-out al objeto:

```python
class Remark(Remark):
    def interpolate_mobject(self, alpha):
        alpha = self.rate_func(alpha)
        self.remark_mob.restore()
        self.remark_mob.scale(interpolate(1,self._scale,alpha))
        # here is the fade-out
        self.remark_mob.fade(alpha)

class Example(Scene):
    def construct(self):
        sq = Square().scale(2)
        self.play(Remark(sq, 1.7))
        self.play(sq.animate.shift(LEFT))
        self.wait()

%manim $_RV
```

## Ejemplo con interpolate_submobject.

Imaginemos que tenemos varios objetos en un vgrp y queremos rotarlos a todos sobre su centro geométrico.

La forma más simple sería hacerlo así (con list comprehesion):

```python
class Example(Scene):
    def construct(self):
        vg = VGroup(Square(),Triangle(),Star())\
            .arrange(RIGHT)
        vg.set(width=config.frame_width-3)
        self.add(vg)
        self.play(*[
                Rotate(mob, 2*PI, about_point=mob.get_center_of_mass())
                for mob in vg
            ],
            run_time=4
        )
        self.wait()

%manim $_RV
```

Pero supongamos que vamos a hacer esto varias veces en nuestra escena, no es muy inteligente repetir el código, por lo que la mejor idea es crear una animación.

Podemos hacerlo con `interpolate_mobject` o con `interpolate_submobject`, dejamos como tarea cómo sería con `interpolate_mobject`, nosotros lo haremos con `interpolate_submobject`.

```python
class RotateEveryMob(Animation):
    def __init__(self, vg, angle=PI/2, rate_func=linear, **kwargs):
        self._angle = angle
        super().__init__(vg, rate_func=rate_func,**kwargs)

    def begin(self):
        # En caso de que necesitemos guardar información
        # sobre cada submob, lo podemos hacer guardándolo
        # como un atributo.
        for mob in self.mobject:
            mob._center = mob.get_center_of_mass()
        super().begin()

    def interpolate_submobject(self, sub, s_sub, alpha):
        # sub = submobject
        # s_sub = starting_submobject
        alpha = self.rate_func(alpha)
        sub.become(s_sub) # is like sub.restore()
        sub.rotate(self._angle * alpha, about_point=sub._center)

class Example(Scene):
    def construct(self):
        vg = VGroup(Square(),Triangle(),Star())\
            .arrange(RIGHT)
        vg.set(width=config.frame_width-3)
        self.add(vg)
        self.play(RotateEveryMob(vg,2*PI,run_time=4))
        self.wait()

%manim $_RV
```

Homework: Añade la opción de que cada submoject cambie a un color específico en caso de que se le indique.

<details>
   <summary> Homework solution </summary>

```python
class RotateEveryMob(Animation):
    def __init__(self, vg, angle=PI/2, rate_func=linear, colors=None,**kwargs):
        self._angle = angle
        if colors is not None:
            assert( len(vg) == len(colors) ) ,"len(vg) not equal to len(colors)"
        self._colors = colors
        super().__init__(vg, rate_func=rate_func,**kwargs)

    def begin(self):
        for i,mob in enumerate(self.mobject):
            mob._center = mob.get_center_of_mass()
            mob._init_color = mob.get_color()
            if self._colors is not None:
                mob._color = self._colors[i]
        super().begin()

    def interpolate_submobject(self, sub, s_sub, alpha):
        alpha = self.rate_func(alpha)
        sub.become(s_sub) # is like sub.restore()
        sub.rotate(self._angle * alpha, about_point=sub._center)
        sub.set_color(interpolate_color(
            sub._init_color, sub._color, alpha
        ))

class Example(Scene):
    def construct(self):
        vg = VGroup(Square(),Triangle(),Star())\
            .arrange(RIGHT)
        vg.set(width=config.frame_width-3)
        self.add(vg)
        self.play(RotateEveryMob(vg,2*PI,colors=[RED,PINK,ORANGE],run_time=4))
        self.wait()

%manim $_RV
```

</details>

## Merge animations.

A veces vas a necesitar fusionar o modificar el comportamiento de una animación solo una vez, por lo que crear una animación personalizada sería una pérdida de tiempo.

En estos casos podemos hacer lo siguiente:

```python
class Example(Scene):
    def construct(self):
        sq = Square().scale(2)

        def merge_anim(mob,color=RED):
            # define anim
            anim = Write(mob, rate_func=linear) # change by there_and_back
            center = mob.get_center_of_mass()
            init_color = mob.get_color()
            # execute begin
            anim.begin()
            def update(mob, alpha):
                anim.interpolate(alpha)
                mob.rotate(PI/2*alpha,about_point=center)
                mob.set_color(interpolate_color(init_color,color,alpha))
            return update

        self.add(sq)
        self.play(UpdateFromAlphaFunc(sq, merge_anim(sq), run_time=3, rate_func=smooth))
        self.wait()

%manim $_RV
```

En caso de quieras fusionar varias animaciones ya existentes puedes hacerlo de la siguiente forma:

```python
class Example(Scene):
    def construct(self):
        sq = Square().scale(2)
        sq.save_state()
        sq._center = sq.get_center_of_mass()

        def merge_anim(mob,alpha):
            mob.restore()
            write_anim = Write(mob, rate_func=linear)
            write_anim.begin()
            write_anim.interpolate(alpha)

            ftc = FadeToColor(mob, RED, rate_func=there_and_back)
            ftc.begin()
            ftc.interpolate(alpha)

            rotate_anim = Rotate(mob, PI/2, about_point=mob._center,rate_func=smooth)
            rotate_anim.begin()
            rotate_anim.interpolate(alpha)

        self.add(sq)
        self.play(UpdateFromAlphaFunc(sq, merge_anim, run_time=3, rate_func=linear))
        self.wait()

%manim $_RV
```

Generalizando, podemos definir una función que haga lo mismo:

```python
def merge_anims(*anims):
    def update(mob, alpha):
        mob.restore()
        for anim_class, anim_kwargs in anims:
            an = anim_class(mob, **anim_kwargs)
            an.begin()
            an.interpolate(alpha)
    return update
```

Es importante resaltar que el orden en el que se definen las animaciones importa, deben de tener en cuenta eso.

```python
class Example(Scene):
    def construct(self):
        sq = Square().scale(2)
        sq.save_state() # <- Don't forget this
        sq._center = sq.get_center_of_mass()

        merge_anim = merge_anims(
            (Write, {"rate_func": linear}),
            (FadeToColor, {"color": RED, "rate_func": there_and_back}),
            (Rotating, {"radians": PI/2, "about_point": sq._center, "rate_func": smooth}),
        )

        self.add(sq)
        self.play(UpdateFromAlphaFunc(sq, merge_anim, run_time=3, rate_func=linear))
        self.wait()

%manim $_RV
```

<!-- ![video](_static/chp2/sol1.mp4) -->