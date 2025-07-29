import pygame as pg
from .game_object import Component
from .vmath_mini import Vector2d
from .surface import SurfaceComponent

class SpriteComponent(Component):
    downloaded: dict[str, pg.Surface] = {}
    texture: pg.Surface
    size: Vector2d

    def __init__(self, path: str = "", size: Vector2d = Vector2d(0, 0), nickname: str = ""):
        prenickname = ":"
        if path != "" and path in SpriteComponent.downloaded:
            self.texture = pg.transform.scale(SpriteComponent.downloaded[path], size.as_tuple())
        elif nickname != "" and (prenickname + nickname) in SpriteComponent.downloaded:
            self.texture = pg.transform.scale(SpriteComponent.downloaded[(prenickname + nickname)], size.as_tuple())
        else:
            if nickname != "":
                SpriteComponent.downloaded[(prenickname + nickname)] = pg.image.load(path)
                self.texture = pg.transform.scale(SpriteComponent.downloaded[(prenickname + nickname)], size.as_tuple())
            else:
                SpriteComponent.downloaded[path] = pg.image.load(path)
                self.texture = pg.transform.scale(SpriteComponent.downloaded[path], size.as_tuple())

    def draw(self):
        surf = self.game_object.get_component(SurfaceComponent)
        surf.pg_surf.blit(self.texture, ((surf.size - Vector2d.from_tuple(self.texture.get_size())) / 2).as_tuple())

    def get_by_nickname(nickname: str) -> pg.Surface:
        prenickname = ":"
        if (prenickname + nickname) in SpriteComponent.downloaded:
            return SpriteComponent.downloaded[(prenickname + nickname)]
        else:
            raise KeyError(f"Sprite with nickname '{nickname}' not found.")