import unittest
from keyboard import make_keyboard_parts
from snapshottest import TestCase


class Snapshots(TestCase):
    def test_default_snapshot(self):
        parts = make_keyboard_parts()
        snapshot = []
        for layout_name_and_part in parts:
            [layout_name, part] = layout_name_and_part
            vertices = [
                (
                    vertice.Center().x,
                    vertice.Center().y,
                    vertice.Center().z,
                )
                for vertice in part.vertices().vals()
            ]
            snapshot.append((layout_name, vertices))

        self.assertMatchSnapshot(snapshot)
