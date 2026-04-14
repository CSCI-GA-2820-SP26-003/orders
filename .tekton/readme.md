# Tekton Local Setup
To set up this pipeline for local development and contribution,
perform the following steps:
1. ensure that you have the openshift cli installed (confirm by running `which oc`)
2. use the openshift dashboard to receive an authentication command to enter into your terminal (go to `help` -> `command line tools` -> `Copy login command`).
3. run the following command to create the necessary resources for the pipeline and application: `oc apply -R -f .tekton -f k8s/postgresql`.
5. update your configuration file and verify its functionality via the openshift sandbox ui
6. confirm your changes by running your pipeline within the dashboard (`pipelines` -> `pipelines` -> `pvc-pipeline` -> `actions` -> `start`)
6. copy the changed portions of your config back to the git-tracked file in the .tekton directory (keep metadata section unchanged)

