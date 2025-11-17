import { apiClient } from './client'
import { Attachment } from '@/types'

class AttachmentsService {
  /**
   * Upload one or more attachments to a mentorship log
   */
  async upload(mentorshipLogId: string, files: FileList | File[]): Promise<Attachment[]> {
    const formData = new FormData()

    // Convert FileList or array to array and append each file
    const fileArray = Array.from(files)
    fileArray.forEach((file) => {
      formData.append('files', file)
    })

    const response = await apiClient.post<Attachment[]>(
      `/api/attachments/upload/${mentorshipLogId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  }

  /**
   * List all attachments for a mentorship log
   */
  async list(mentorshipLogId: string): Promise<Attachment[]> {
    const response = await apiClient.get<Attachment[]>(
      `/api/attachments/${mentorshipLogId}`
    )
    return response.data
  }

  /**
   * Delete an attachment
   */
  async delete(attachmentId: string): Promise<void> {
    await apiClient.delete(`/api/attachments/${attachmentId}`)
  }

  /**
   * Get download URL for an attachment
   */
  getDownloadUrl(attachmentId: string): string {
    return `${process.env.NEXT_PUBLIC_API_URL}/api/attachments/download/${attachmentId}`
  }
}

export const attachmentsService = new AttachmentsService()
