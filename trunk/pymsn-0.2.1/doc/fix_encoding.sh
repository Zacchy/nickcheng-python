#!/bin/sh

sed -i \
    's/<?xml version="1.0" encoding="iso-8859-1"?>/<?xml version="1.0" encoding="utf-8"?>/' \
    $@
    
sed -i \
    's/<?xml version="1.0" encoding="ascii"?>/<?xml version="1.0" encoding="utf-8"?>/' \
    $@
