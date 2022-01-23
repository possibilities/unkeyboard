* `npx nodemon --exec 'flake8 . --builtins="show_object" --max-line-length=88 --extend-ignore=E203,E501 && vulture .' --watch . --ext 'py'`
* `pytest-watch -- --capture no -vv --disable-warnings --workers auto`
* `while cq-editor case_and_pcb.py || true ; do ; done ;`
  * needed while cq-editor crashes frequently
* `npx nodemon --exec 'pcbnew data/pcb/keyboard.kicad_pcb' --watch data/pcb/keyboard.kicad_pcb`
* `SHOW_PATHS_ONLY=1 npx nodemon pcb.py --ext='py'`
