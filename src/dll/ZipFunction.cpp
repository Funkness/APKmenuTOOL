#include "stdafx.h"
#include "ZipFunction.h"
#include <io.h>
#include <Shlobj.h>


ZRESULT CZipFunction::ExtractApkToDir(LPCTSTR lpszZipFullName, LPCTSTR lpszUnZipPath,CString szPackageName,list<CString>& fileName,LPCTSTR fileType)
{
	TCHAR buffer[MAX_PATH] = {0};
	CString strUnZipPath = lpszUnZipPath;
	DWORD zResult = ZR_OK;
	CString strfile = _T("");
	CString szPushFile = _T("");
		

	if (!strUnZipPath.IsEmpty())
	{
		// ����ļ�·���������ȴ���,���ڲ����κ��޸�
		SHCreateDirectoryEx(NULL, lpszUnZipPath, NULL);
	}
	else
	{
		//AfxMessageBox(_T("apkoutĿ¼������"));
	}

	HZIP hz = OpenZip(lpszZipFullName, 0);
	ZIPENTRY ze;

	GetZipItem(hz, -1, &ze); 
	int numitems = ze.index;

	for (int zi = 0; zi < numitems; zi++)
	{ 
		ZIPENTRY ze;
		GetZipItem(hz,zi,&ze); 
		strfile = ze.name;
		if (strfile.Find('/')!=-1)
			continue;
		if (strfile.Find(fileType)==-1)
			continue;

		zResult = UnzipItem(hz, zi, (CString)strUnZipPath+_T("\\")+szPackageName+_T("_")+ze.name);  
		szPushFile = szPackageName+_T("_");
		szPushFile += ze.name;
		fileName.push_back(szPushFile);

		szPushFile = _T("");
			
		if (zResult != ZR_OK)
		{
			//AfxMessageBox(_T("��ѹ�ļ�����"));
		}
	}
	CloseZip(hz);
	return zResult;
}

	
ZRESULT CZipFunction::DirToZip(LPCTSTR lpszSrcPath, LPCTSTR lpszZipName, HZIP& hz, LPCTSTR lpszDestPath)
{
	static int nCount = 0;
	static CString strFileName;
	nCount++;
	DWORD zResult = ZR_OK;
	TCHAR buffer[MAX_PATH] = {0};
	CString szTempFile;

	CString strDestPath = lpszDestPath;

	szTempFile = strFileName;

	if (nCount == 1)
	{
		// ����ߵ�ִֻ��һ��
		if (!strDestPath.IsEmpty())
		{
			// �����ѹ·���ļ��в����� �ȴ���,���� �����κ��޸�
			SHCreateDirectoryEx(NULL, lpszDestPath, NULL);
		}
		else
		{
			GetCurrentDirectory(MAX_PATH, (LPTSTR)&buffer);
			strDestPath = buffer;
			SHCreateDirectoryEx(NULL, strDestPath, NULL);
		}
		hz = CreateZip((CString)strDestPath+_T("\\")+(CString)lpszZipName, 0);
	}

	HANDLE file;
	WIN32_FIND_DATA fileData;
	file = FindFirstFile((CString)lpszSrcPath+_T("\\*.*"), &fileData);
	FindNextFile(file, &fileData);
	while (FindNextFile(file, &fileData))
	{
		// �����һ���ļ�Ŀ¼
		if(fileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
		{
			if (strFileName.IsEmpty())
			{
				ZipAddFolder(hz, fileData.cFileName);
			}
			else
			{
				ZipAddFolder(hz, strFileName+_T("\\")+fileData.cFileName);
			}
			if (!strFileName.IsEmpty())
			{
				strFileName += _T("\\");
			}
				
			strFileName += fileData.cFileName;
			// �������ļ��� �ݹ����
			DirToZip((CString)lpszSrcPath+_T("\\")+ fileData.cFileName, lpszZipName, hz, lpszDestPath);
			//strFileName.Empty();
			strFileName = szTempFile; 
		}
		else
		{
			CString strTempPath;
			strTempPath.Format(_T("%s\\%s"), (CString)lpszSrcPath, fileData.cFileName);
			if (strFileName.IsEmpty())
			{
				ZipAdd(hz, fileData.cFileName, strTempPath);
			}
			else
			{
				ZipAdd(hz, strFileName+_T("\\")+fileData.cFileName, strTempPath);
			}

			if (zResult != ZR_OK)
			{
				return zResult;
			}
		}
	}

	FindClose(file);
	strFileName.Empty();
	return zResult;
}

ZRESULT CZipFunction::CompressDirToZip(LPCTSTR lpszSrcPath, LPCTSTR lpszZipName, LPCTSTR lpszDestPath)
{
	HZIP hz;
	DWORD zResult = ZR_OK;
	zResult = DirToZip(lpszSrcPath, lpszZipName,hz, lpszDestPath);
	if(zResult == ZR_OK)
	{
		CloseZip(hz);
	}
	return zResult;
}