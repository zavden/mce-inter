# alpha updaters

## Concept

$\alpha$ updaters are a quick way to create custom animations.
They are used when you need to perform a very specific animation a few times. In case you need to apply that animation many times, it is best to create a custom animation, we will see this in the next chapter.

The $\alpha$  parameter basically represents the `run_time` progress of a `rate_function`.

If you have an animation like this:

```python
Scene.play(Animation(mob,run_time=5,rate_func=smooth))
```

So $\alpha$ at 20% is 1 second, $\alpha$ at 50% is 2.5 seconds, and $\alpha$ at 100% is 5 seconds.

/insert image

That's what the $\alpha$ parameter means in animations.

To define an $\alpha$ updater you have to obey the following format:

```python
def my_alpha_updater(mob, alpha): # mob, vmob, grp, vgr. etc
    color = interpolate_color(RED,BLUE,alpha)
    mob.set_color(color)
```

$\alpha$ updaters are functions that receive as parameters a single Mobject, followed by the alpha parameter. It is mandatory that the second parameter be called alpha, so that Manim interprets it correctly.

In the code above we are animating the color change from `RED` to `BLUE`.

At start, $\alpha$, so mob is going to be `RED`, if we're using a `rate_func` like linear or smooth, when $\alpha=0.5$ then the color will be purple. And when the animation ends (if we're using a rate_func like linear or smooth) then the color will be `BLUE`.

The way to use an $\alpha$ updater is as follows:

```python
square = Square()

Scene.play(
    UpdateFromAlphaFunc(square, my_alpha_updater,run_time=4,rate_func=smooth)
)
```

The `UpdateFromAlphaFunc` animation receives as its first argument the Mobject to which the updater is going to be applied, and as its second argument the updater. And like any animation it receives `run_time`, `rate_func` and remove.

The complete code is like this:

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

## Pro-tip 1: Closure

If we use the concept of Closure (as we saw in the previous course) then we could do something like this:

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

A very quick (limited, and inelegant) way to create custom animations is like this:

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

In the next chapter we will see the best way to create custom animations.

## Pro-tip 2: How to use save_state and interpolate with alpha updaters.

In the previous course we saw that it's not a good idea to use the Transform animation to animate rotations, but alpha updaters are great for doing rotations.

You may be tempted to do it like this:



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

But we see that this does not work, this is because each frame of the animation we are rotating `40 * DEGREES * alpha`, that is, if we render this at 60fps:

* Frame 1 (alpha=0/60): angle = 40 * DEGREES * 0/60 = 0.0 * DEGREES
* Frame 2 (alpha=1/60): angle = 40 * DEGREES * 1/60 = 0.66 * DEGREES
* Frame 3 (alpha=2/60): angle = 40 * DEGREES * 2/60 = 1.33 * DEGREES
* Frame 4 (alpha=3/60): angle = 40 * DEGREES * 3/60 = 2.0 * DEGREES
* Frame 5 (alpha=4/60): angle = 40 * DEGREES * 4/60 = 2.66 * DEGREES
* Frame 6 (alpha=5/60): angle = 40 * DEGREES * 5/60 = 3.33 * DEGREES

That is, each frame that passes the angle of rotation increases, which is not desired.

To solve this we have to "remember" the initial state of the Mobject, so that, each frame start, it is restored to the initial state, and then we apply the angle to it.

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

A function that is often quite used together with alpha updaters is interpolate, which, as its name suggests, interpolates a value between two extremes, using an alpha parameter (similar to interpolate_color). We will understand it better with the following example.

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