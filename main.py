import ppb
from ppb import keycodes, systemslib
from ppb.events import KeyPressed, KeyReleased
from dataclasses import dataclass


class Player(ppb.Sprite):
    position = ppb.Vector(0, -3)
    direction = ppb.Vector(0, 0)
    speed = 4
    left = keycodes.Left
    right = keycodes.Right
    projector = keycodes.Space

    def on_update(self, update_event, signal):
        self.position += self.direction * self.speed * update_event.time_delta

    def on_key_pressed(self, key_event: KeyPressed, signal):
        if key_event.key == self.left:
            self.direction += ppb.Vector(-1, 0)
        elif key_event.key == self.right:
            self.direction += ppb.Vector(1, 0)
        elif key_event.key == self.projector:
            key_event.scene.add(Projectile(position=self.position + ppb.Vector(0, 0.5)))

    def on_key_released(self, key_event: KeyReleased, signal):
        if key_event.key == self.left:
            self.direction += ppb.Vector(1, 0)
        elif key_event.key == self.right:
            self.direction += ppb.Vector(-1, 0)


class Projectile(ppb.Sprite):
    size = 0.25
    direction = ppb.Vector(0, 1)
    speed = 6

    def on_update(self, update_event, signal):
        if self.direction:
            direction = self.direction.normalize()
        else:
            direction = self.direction
        self.position += direction * self.speed * update_event.time_delta


class Target(ppb.Sprite):
    points = 10

    def on_update(self, update_event, signal):
        for p in update_event.scene.get(kind=Projectile):
            if (p.position - self.position).length <= self.size:
                update_event.scene.remove(self)
                update_event.scene.remove(p)
                signal(TargetDestroyed(self))
                break
            

@dataclass
class TargetDestroyed:
    target: Target


class ScoreDisplay(ppb.RectangleSprite):
    score = 0
    layer = 100
    offset = ppb.Vector(0, 0)

    @property
    def image(self):
        return ppb.Text(f"Score: {self.score}", font=ppb.Font("Comfortaa_Bold.ttf", size=72), color=(255, 255, 255))

    def on_pre_render(self, event: ppb.events.PreRender, signal):
        self.position = event.scene.main_camera.position + self.offset


class ScoreSystem(systemslib.System):
    top_score = 0
    last_score = 0
    current_score = 0

    def __enter__(self):
        pass  # load up existing high score if available

    def on_target_destroyed(self, event: TargetDestroyed, signal):
        self.current_score += event.target.points

    def on_scene_started(self, event: ppb.events.SceneStarted, signal):
        event.scene.top_score = self.top_score
        event.scene.last_score = self.last_score

    def on_pre_render(self, event, signal):
        for score_display in event.scene.get(kind=ScoreDisplay):
            score_display.score = self.current_score


def setup(scene):
    scene.add(Player())
    scene.add(ScoreDisplay(offset=ppb.Vector(-4, 5)))

    for x in range(-4, 5, 2):
        scene.add(Target(position=ppb.Vector(x, 3)))


ppb.run(setup=setup, systems=[ScoreSystem])
