"""User data isolation: cross-tenant access must always 404."""
from __future__ import annotations


def test_other_user_cannot_read_project(client, auth_b, analyzed_project):
    resp = client.get(f"/api/projects/{analyzed_project['id']}", headers=auth_b)
    assert resp.status_code == 404


def test_other_user_cannot_list_someone_elses_clips(client, auth_b, analyzed_project):
    resp = client.get(f"/api/projects/{analyzed_project['id']}/clips", headers=auth_b)
    assert resp.status_code == 404


def test_other_user_cannot_delete_or_render(client, auth_b, analyzed_project):
    assert client.delete(f"/api/projects/{analyzed_project['id']}", headers=auth_b).status_code == 404
    assert (
        client.post(f"/api/projects/{analyzed_project['id']}/render", headers=auth_b, json={}).status_code
        == 404
    )


def test_other_user_cannot_reach_media_key(client, auth_b, analyzed_project):
    key = f"{analyzed_project['id']}/anything.mp4"
    resp = client.get(f"/media/{key}", headers=auth_b)
    assert resp.status_code == 404


def test_unauthenticated_media_is_blocked(client):
    client.cookies.clear()
    assert client.get("/media/whatever/file.mp4").status_code == 401
