@rem 记得先输入 npm run build

del "../static"
ren dist static
move "static" "../"
