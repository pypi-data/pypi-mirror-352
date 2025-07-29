#! /usr/bin/env bash

function bluer_objects_mlflow_deploy() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_local=$(bluer_ai_option_int "$options" local 1)
    local port=$(bluer_ai_option "$options" port 5001)

    if [[ "$do_local" == 0 ]]; then
        bluer_ai_log_error "only local deployment is supported."
        return 1
    fi

    [[ "$MLFLOW_DEPLOYMENT" != "local" ]] &&
        bluer_ai_log_warning "MLFLOW_DEPLOYMENT is not local".

    bluer_ai_badge "🤖"

    bluer_ai_eval dryrun=$do_dryrun \
        mlflow ui \
        --backend-store-uri $MLFLOW_TRACKING_URI \
        --default-artifact-root file://$MLFLOW_TRACKING_URI \
        --host 0.0.0.0 \
        --port $port

    bluer_ai_badge "💻"
}
