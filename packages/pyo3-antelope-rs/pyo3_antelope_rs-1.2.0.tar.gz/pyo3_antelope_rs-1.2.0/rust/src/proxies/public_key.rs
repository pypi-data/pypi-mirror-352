use crate::impl_packable_py;
use crate::proxies::private_key::PrivateKey;
use antelope::chain::public_key::{PublicKey as NativePublicKey, PublicKeyParsingError};
use antelope::serializer::Packer;
use pyo3::basic::CompareOp;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::hash::{DefaultHasher, Hash, Hasher};
use std::str::FromStr;

#[pyclass]
#[derive(Debug, Clone)]
pub struct PublicKey {
    pub inner: NativePublicKey,
}

impl_packable_py! {
    impl PublicKey(NativePublicKey) {
        #[staticmethod]
        fn from_str(s: &str) -> PyResult<Self> {
            Ok(PublicKey{
                inner: NativePublicKey::from_str(s)
                    .map_err(|e| PyValueError::new_err(e.to_string()))?
            })
        }

        pub fn value(&self) -> &[u8] {
            self.inner.value.as_slice()
        }

        fn __str__(&self) -> String {
            self.inner.as_string()
        }

        fn __hash__(&self) -> u64 {
            let mut h = DefaultHasher::new();
            self.inner.key_type.to_index().hash(&mut h);
            self.inner.value.hash(&mut h);
            h.finish()
        }

        fn __richcmp__(&self, other: &PublicKey, op: CompareOp) -> PyResult<bool> {
            match op {
                CompareOp::Eq => Ok(self.inner == other.inner),
                CompareOp::Ne => Ok(self.inner != other.inner),
                _ => Err(pyo3::exceptions::PyNotImplementedError::new_err(
                    "Operation not implemented",
                )),
            }
        }
    }
}

impl TryFrom<&PrivateKey> for PublicKey {
    type Error = PublicKeyParsingError;
    fn try_from(value: &PrivateKey) -> Result<Self, Self::Error> {
        Ok(Self {
            inner: value.inner.to_public()?
        })
    }
}
