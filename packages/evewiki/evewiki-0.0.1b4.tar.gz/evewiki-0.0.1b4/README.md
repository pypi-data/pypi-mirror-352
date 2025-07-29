# evewiki

Wiki plugin for [AllianceAuth](https://gitlab.com/allianceauth/allianceauth) to curate content.

[Documentation](./docs/index.md)

## Features

- Collaborative editing for editors
- Create and organise pages in a hierarchical structure using `slugs`
- Supports markdown with both rich and raw editing modes
- Version History
- Event logging
- Restrict content by user's `groups` and/or `states`
- Publish public pages

## Installation

### Step 1 - Pre_Requisites

Evewiki is an App for Alliance Auth, Please make sure you have this installed. Evewiki is not a standalone Django Application

### Step 2 - Install app

pip install evewiki

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add `evewiki` to `INSTALLED_APPS` in `local.py`

```python
INSTALLED_APPS += [
	'evewiki',
...
```

- Optional: Add `evewiki` to `APPS_WITH_PUBLIC_VIEWS` in `local.py`
To enable public pages
```python
APPS_WITH_PUBLIC_VIEWS = [
    'evewiki',
]
```

### Step 4 - Maintain Alliance Auth

Run migrations `python manage.py migrate`
Restart Alliance Auth

### Step 5

In AA admin site add Permissions
- `evewiki | general | Can access this app`
- `evewiki | general | Can edit this app`
to the desired `States` / `Groups`

i.e. you may wish to create a `wiki_editors` group to restrict the `Can edit this app` controls.

## Permissions

Users need to have at least `basic_access` interactions with the application

| Name                  | Description                                              |
|-----------------------|----------------------------------------------------------|
| `basic_access`        | Basic access to load content                             |
| `editor_access`       | Grant the necessary controls and access to edit content  |


## Settings

List of settings that can be modified for the application
You can alter them by adding a record to the `Settings` section/table in the `evewiki` section of the Admin site

| Name                          | Description                                                                                      | Default |
|-------------------------------|--------------------------------------------------------------------------------------------------|---------|
| `hierarchy_max_display_depth` | Limit the depth of the tree for the hierarchy on the main display                                | 10      |
| `max_versions`                | No one has infinite disk space, a sensible limit which can be modified to clear down the history | 1000    |

# Screenshots

**View Mode**

![View Mode](https://imgur.com/Y4mZHzm)

**Edit Mode**

![Edit Mode](https://imgur.com/cRWFq3W)

**Raw Mode**

![Raw Mode](https://imgur.com/WBvP97N)

**Page Details**

![Page Details](https://imgur.com/1iO0ciu)

**Public badge**

![Public](https://imgur.com/Ps0tkr8)
