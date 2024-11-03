package com.example.projectvesion

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.lifecycle.findViewTreeViewModelStoreOwner

import com.example.version60.R
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
//import kotlinx.coroutines.NonCancellable.message
import kotlinx.coroutines.launch
import okhttp3.Callback
import okhttp3.FormBody
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody


class UploadData : Fragment() {

    private val apiToken = "b5721c78-875d-4608-a482-72a6bc62122b"
    private val apiUrl = "http://176.214.202.28:5000/askQuestion"

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_upload_data, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val fileBT: Button = view.findViewById(R.id.fileBT)

        fileBT.setOnClickListener {
            val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
                type = "application/pdf"
                addCategory(Intent.CATEGORY_OPENABLE)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivityForResult(intent, 1)
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        // Добавьте аннотацию @Deprecated, если используете более новые версии SDK
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 1 && resultCode == Activity.RESULT_OK) {
            data?.data?.let { uri ->
                // Получаем имя файла
                val fileName = getFileName(uri)
                Toast.makeText(requireContext(), "Выбрано: $fileName", Toast.LENGTH_SHORT).show()

                // Отправляем файл на сервер
                uploadFileToServer(uri, fileName)
            }
        }
    }

    private fun getFileName(uri: Uri): String {
        var result: String? = null
        if (uri.scheme == "content") {
            val cursor = requireContext().contentResolver.query(uri, null, null, null, null)
            cursor?.use {
                if (it.moveToFirst()) {
                    result = it.getString(it.getColumnIndexOrThrow(OpenableColumns.DISPLAY_NAME))
                }
            }
        }
        if (result == null) {
            result = uri.path
            val cut = result?.lastIndexOf('/') ?: -1
            if (cut != -1) {
                result = result?.substring(cut + 1)
            }
        }
        return result ?: "filename.pdf"
    }

    private fun uploadFileToServer(uri: Uri, fileName: String) {
        // Используем OkHttp для отправки файла
        val client = OkHttpClient()

        // Получаем InputStream из Uri
        val inputStream = requireContext().contentResolver.openInputStream(uri)

        // Читаем файл в ByteArray
        val fileBytes = inputStream?.readBytes()
        inputStream?.close()

        if (fileBytes == null) {
            Toast.makeText(requireContext(), "Не удалось прочитать файл", Toast.LENGTH_SHORT).show()
            return
        }

        // Создаем RequestBody для файла
        val fileBody = fileBytes.toRequestBody("application/pdf".toMediaTypeOrNull())

        // Создаем MultipartBody для отправки файла
        val multipartBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", fileName, fileBody)
            .build()

        // Создаем запрос
        val request = Request.Builder()
            .url(apiUrl)
            .addHeader("Authorization", "Bearer $apiToken") // Добавляем API-токен в заголовок
            .post(multipartBody)
            .build()

        // Отправляем запрос в фоновом потоке
        Thread {
            try {
                val response = client.newCall(request).execute()
                val responseBody = response.body?.string()

                // Обновляем UI в главном потоке
                requireActivity().runOnUiThread {
                    if (response.isSuccessful) {
                        Toast.makeText(requireContext(), "Файл успешно отправлен", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(requireContext(), "Ошибка отправки файла: $responseBody", Toast.LENGTH_LONG).show()
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
                requireActivity().runOnUiThread {
                    Toast.makeText(requireContext(), "Ошибка: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }.start()
    }

    companion object {
        @JvmStatic
        fun newInstance() = UploadData()
    }
}