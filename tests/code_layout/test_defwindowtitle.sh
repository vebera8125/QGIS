#!/usr/bin/env bash

# This test checks that dialogs have a non-default window title or it is not marked for translation

if git grep -E -B1 '<string>(Form|Dialog)</string>' "*.ui" | grep -qs '<property name="windowTitle"'; then
  echo ' *** Found ui with default window title - consider changing or unchecking "translatable"/adding notr="true"'
  git grep -E -B1 '<string>(Form|Dialog)</string>' "*.ui" | grep -A1 '<property name="windowTitle"'
  exit 1
fi

