
path "transit/keys/KEK_*" {
capabilities = ["read"]
}
path "/transit/datakey/plaintext/KEK_*" {
capabilities = ["update"]
}
path "transit/decrypt/KEK_*" {
capabilities = [ "update"]
}
