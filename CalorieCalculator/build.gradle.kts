// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    alias(libs.plugins.android.application) apply false

    // DÜZELTME 1: libs dosyasında ismini "jetbrains-kotlin-android" yaptık, burada da öyle çağırmalıyız
    alias(libs.plugins.jetbrains.kotlin.android) apply false

    // DÜZELTME 2: "kotlin.compose" satırını SİLDİK.
    // Çünkü "compose.compiler" ile aynı işi yapıyor ve çakışıyordu.

    // DÜZELTME 3: Kotlin 2.0 için gerekli olan compiler plugini
    alias(libs.plugins.compose.compiler) apply false
}