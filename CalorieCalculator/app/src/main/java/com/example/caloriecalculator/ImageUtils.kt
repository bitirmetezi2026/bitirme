package com.example.caloriecalculator

import android.content.Context
import android.graphics.Bitmap
import android.net.Uri
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream

object ImageUtils {

    fun bitmapToMultipart(bitmap: Bitmap, context: Context): MultipartBody.Part {
        val file = File(context.cacheDir, "camera_image_${System.currentTimeMillis()}.jpg")
        file.createNewFile()

        val bos = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, bos)
        val bitmapData = bos.toByteArray()

        FileOutputStream(file).use { fos ->
            fos.write(bitmapData)
            fos.flush()
        }

        val requestFile = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
        // DİKKAT: Buradaki "file" ismi, NetworkManager'daki @Part ismiyle AYNI olmalı
        return MultipartBody.Part.createFormData("file", file.name, requestFile)
    }

    fun uriToMultipart(uri: Uri, context: Context): MultipartBody.Part? {
        return try {
            val inputStream = context.contentResolver.openInputStream(uri) ?: return null
            val tempFile = File(context.cacheDir, "gallery_image_${System.currentTimeMillis()}.jpg")

            FileOutputStream(tempFile).use { outputStream ->
                inputStream.copyTo(outputStream)
            }

            val requestFile = tempFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
            // DİKKAT: Buradaki "file" ismi, NetworkManager'daki @Part ismiyle AYNI olmalı
            return MultipartBody.Part.createFormData("file", tempFile.name, requestFile)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}