#! /usr/bin/env bash

function bluer_objects_upload() {
    local options=$1
    local filename=$(bluer_ai_option "$options" filename)

    local object_name=$(bluer_ai_clarify_object $2 .)
    local object_path=$ABCLI_OBJECT_ROOT/$object_name

    rm -rf $object_path/auxiliary

    python3 -m bluer_objects.storage \
        upload \
        --object_name $object_name \
        --filename "$filename"
    [[ $? -ne 0 ]] && return 1

    if [[ -z "$filename" ]]; then
        bluer_objects_mlflow_log_run $object_name
    fi
}
