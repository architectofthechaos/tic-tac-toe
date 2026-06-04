{{/*
Chart name, optionally truncated to 63 chars for DNS-safe names.
*/}}
{{- define "tic-tac-toe.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Fully qualified app name: <release>-<chart>, truncated to 63 chars.
*/}}
{{- define "tic-tac-toe.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels applied to all resources.
*/}}
{{- define "tic-tac-toe.labels" -}}
app.kubernetes.io/name: {{ include "tic-tac-toe.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{/*
Selector labels — shared by the Deployment pod template and the Service selector.
*/}}
{{- define "tic-tac-toe.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tic-tac-toe.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
